"""
前端特性演示专用 Mock FastAPI 服务

启动方式:
  cd frontend/test
  pip install fastapi uvicorn pydantic
  python main.py

然后在另一终端启动前端:
  cd frontend
  node app.js

访问 http://localhost:3000 即可体验全部前端特性
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn
import asyncio

app = FastAPI(title="AI Agent Mock API")


# ============ 数据模型 ============
class UserInput(BaseModel):
    msg: str
    type: str = "text"


class RefItem(BaseModel):
    txt: str
    link: str


class AgentResponse(BaseModel):
    flow: str
    refs: List[RefItem]


# ============ 演示数据：展示前端全部特性 ============

DEMO_FLOW = '''\
### 🧠 LangChain 思考过程：

**用户意图分析**：检测到用户询问「{query}」，需要调用多个工具进行检索与推理。

---

1. **启动语义检索** — 正在查询向量数据库...
2. **调用 Web Search 工具** — 从互联网获取最新资料
3. **知识融合** — 合并本地知识库与在线结果
4. **生成最终答案** — 使用 GPT-4 进行总结

---

以下是检索到的示例代码：

```python
from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI

# 初始化工具
tools = [
    Tool(name="Search", func=search_func, description="搜索互联网"),
    Tool(name="Calculator", func=calc_func, description="数学计算"),
]

# 创建 Agent
agent = initialize_agent(tools, OpenAI(), agent="zero-shot-react-description")
result = agent.run("今天北京天气怎么样？")
print(result)
```

> 💡 **提示**：以上代码演示了如何使用 LangChain 构建一个简单的 ReAct Agent。

---

**结论**：根据检索结果，已为您整合了相关信息。如需深入了解，请参考右侧「知识库引用」。
'''

DEMO_REFS = [
    RefItem(txt="📘 LangChain 官方文档", link="https://python.langchain.com/docs"),
    RefItem(txt="🚀 FastAPI 教程", link="https://fastapi.tiangolo.com/tutorial/"),
    RefItem(txt="🧪 LangGraph 多智能体", link="https://langchain-ai.github.io/langgraph/"),
    RefItem(txt="📦 Pydantic 数据校验", link="https://docs.pydantic.dev/latest/"),
]


# ============ 核心接口 ============
@app.post("/api/chat", response_model=AgentResponse)
async def chat_endpoint(user_input: UserInput):
    """
    模拟 AI Agent 响应，返回:
    - flow: 带 Markdown 的思维链日志（含标题/列表/代码块/引用块）
    - refs: 知识库引用列表
    """
    print(f"✅ 收到请求: {user_input.msg}")

    # 模拟 LLM 处理延迟（1.5 秒）
    await asyncio.sleep(1.5)

    return AgentResponse(
        flow=DEMO_FLOW.format(query=user_input.msg),
        refs=DEMO_REFS,
    )


@app.get("/")
async def root():
    return {"status": "ok", "message": "Mock API 运行中，请访问 http://localhost:3000"}


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Mock FastAPI 服务启动中...")
    print("   API 地址: http://127.0.0.1:8000")
    print("   前端地址: http://localhost:3000 (需另行启动 node app.js)")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)