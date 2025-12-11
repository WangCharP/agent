from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import time

app = FastAPI()

# 1. 定义请求模型 (对应前端发来的 JSON)
class UserInput(BaseModel):
    msg: str
    type: str = "text"

# 2. 定义响应模型 (对应前端需要的 JSON)
class AvatarState(BaseModel):
    state: str
    mood: str

class RefItem(BaseModel):
    txt: str
    link: str

class AgentResponse(BaseModel):
    avatar: AvatarState
    flow: str
    refs: List[RefItem]

# 3. 核心接口
@app.post("/api/chat", response_model=AgentResponse)
async def chat_endpoint(user_input: UserInput):
    
    # ===这里接入你的 LangChain 逻辑===
    print(f"收到指令: {user_input.msg}")
    
    # 模拟 LangChain 处理延迟
    time.sleep(1) 
    
    # 模拟返回结果
    return AgentResponse(
        avatar=AvatarState(state="speaking", mood="happy"),
        flow=f"LangChain 思考过程:\n1. 解析意图: {user_input.msg}\n2. 调用工具: VectorStore\n3. 生成答案...",
        refs=[
            RefItem(txt="LangChain文档", link="https://python.langchain.com"),
            RefItem(txt="FastAPI官网", link="https://fastapi.tiangolo.com")
        ]
    )

if __name__ == "__main__":
    # 启动在 8000 端口
    uvicorn.run(app, host="0.0.0.0", port=8000)