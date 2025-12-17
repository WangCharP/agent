import asyncio
from openai import AsyncOpenAI
from app.config import settings
from kg_agent.tools.search import SearchTool

class ChatService:
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL
            )
        self.search_tool = SearchTool()

    async def chat(self, msg: str):
        if not self.client:
            # Fallback if no key
            await asyncio.sleep(1)
            return {"flow": f"**Error**: No OpenAI API Key provided. Please set OPENAI_API_KEY in .env.\n\nYou said: {msg}", "refs": []}

        try:
            # 1. 执行搜索
            search_results = self.search_tool.search(msg)
            
            # 2. 整理上下文
            context = ""
            refs = []
            if search_results:
                context = "Search Results:\n"
                for i, res in enumerate(search_results):
                    context += f"{i+1}. {res['title']}: {res['content']}\n"
                    refs.append({"txt": res['title'], "link": res['url']})
            
            # 3. 构建 Prompt
            system_prompt = "You are a helpful AI assistant. Please answer the user's question based on the provided search results. If the search results are not relevant, answer based on your own knowledge. Format your answer in Markdown."
            user_prompt = f"User Question: {msg}\n\n{context}"

            # 4. 调用 LLM
            response = await self.client.chat.completions.create(
                model=settings.SMART_LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            return {
                "flow": response.choices[0].message.content,
                "refs": refs
            }
            
        except Exception as e:
            return {"flow": f"**Error calling LLM**: {str(e)}", "refs": []}
