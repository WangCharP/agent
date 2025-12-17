import asyncio
from openai import AsyncOpenAI
from app.config import settings
from kg_agent.prompts.chat_prompts import ChatPrompts
from app.utils.stream_utils import StreamFormatter

# Mock Search (如果你没装 Tavily，这个 Mock 保证能跑)
try:
    from kg_agent.tools.search import SearchTool
except ImportError:
    class SearchTool:
        def search(self, query):
            return [
                {"title": f"关于 {query} 的技术文档", "content": f"Mock Data: 这是 {query} 的技术细节...", "url": "http://mock-tech.com"},
                {"title": f"{query} 行业新闻", "content": f"Mock Data: {query} 的最新动态...", "url": "http://mock-news.com"}
            ]

class ChatService:
    def __init__(self):
        self.search_tool = SearchTool()

    def _get_client(self, config: dict) -> AsyncOpenAI:
        if not config.get("api_key"):
            raise ValueError(f"Missing API Key")
        return AsyncOpenAI(api_key=config["api_key"], base_url=config["base_url"])

    async def _run_single_model_pipeline(self, model_name: str, model_config: dict, user_msg: str):
        client = None
        try:
            client = self._get_client(model_config)
            
            # --- 1. 生成搜索词 ---
            is_reasoner = "reasoner" in model_name.lower()
            msgs = []
            # R1 兼容性处理
            if is_reasoner:
                msgs = [{"role": "user", "content": ChatPrompts.QUERY_GEN_SYSTEM + f"\n\n用户问题: {user_msg}"}]
            else:
                msgs = [{"role": "system", "content": ChatPrompts.QUERY_GEN_SYSTEM}, {"role": "user", "content": user_msg}]

            q_res = await client.chat.completions.create(model=model_name, messages=msgs)
            search_query = q_res.choices[0].message.content.strip().replace('"', '')
            
            # --- 2. 搜索 ---
            raw_results = await asyncio.to_thread(self.search_tool.search, search_query)
            if not raw_results:
                return {"model": model_name, "search_query": search_query, "summary": "未找到结果", "refs": []}

            # --- 3. 总结 ---
            context_str = "\n".join([f"Title: {r.get('title')}\nContent: {r.get('content')}" for r in raw_results[:3]])
            summary_prompt = ChatPrompts.build_summary_user(user_msg, context_str)
            
            sum_msgs = []
            if is_reasoner:
                 sum_msgs = [{"role": "user", "content": ChatPrompts.SUMMARY_SYSTEM + f"\n\n{summary_prompt}"}]
            else:
                sum_msgs = [{"role": "system", "content": ChatPrompts.SUMMARY_SYSTEM}, {"role": "user", "content": summary_prompt}]

            s_res = await client.chat.completions.create(model=model_name, messages=sum_msgs)
            
            return {
                "model": model_name,
                "search_query": search_query,
                "summary": s_res.choices[0].message.content,
                "refs": raw_results
            }
        except Exception as e:
            return {"model": model_name, "search_query": "Error", "summary": f"Error: {str(e)}", "refs": []}
        finally:
            if client: await client.close()

    async def chat_stream(self, msg: str):
        search_models = settings.SEARCH_MODELS
        if not search_models:
            yield StreamFormatter.format("error", "未配置搜索模型，请检查 .env")
            return

        yield StreamFormatter.format("status", f"正在唤醒 {len(search_models)} 个 AI 专家进行并行侦查...")

        # 并行执行
        tasks = [self._run_single_model_pipeline(name, conf, msg) for name, conf in search_models.items()]
        results = await asyncio.gather(*tasks)

        yield StreamFormatter.format("status", "多模型侦查结束，正在合并情报...")
        
        reports, all_refs = [], []
        for res in results:
            # 推送每个模型的完成状态，让前端显示
            yield StreamFormatter.format("status", f"=== 专家报告 ({res['model']}) 已生成 ===")
            
            for item in res['refs']:
                all_refs.append({"title": f"[{res['model']}] {item.get('title')}", "url": item.get('url', '#')})
            reports.append(f"=== 专家报告 ({res['model']}) ===\n搜索词: {res['search_query']}\n结论: {res['summary']}\n")

        yield StreamFormatter.format("sources", all_refs)
        yield StreamFormatter.format("status", "首席分析师正在生成最终综合报告...")

        # 最终汇总
        solver_conf = settings.SOLVER_MODEL
        solver_client = self._get_client(solver_conf["config"])
        try:
            stream = await solver_client.chat.completions.create(
                model=solver_conf["name"],
                messages=[
                    {"role": "system", "content": ChatPrompts.SOLVER_SYSTEM},
                    {"role": "user", "content": ChatPrompts.build_solver_user(msg, reports)}
                ],
                stream=True
            )
            async for chunk in stream:
                if content := chunk.choices[0].delta.content:
                    yield StreamFormatter.format("content", content)
        finally:
            await solver_client.close()