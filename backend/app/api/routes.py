from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.schemas.request import ChatRequest
from app.service.chat_service import ChatService
from app.config import settings
import os

app = FastAPI()

# 实例化服务
chat_service = ChatService()

@app.post("/api/chat")
async def chat(request: ChatRequest):
    result = await chat_service.chat(request.msg)
    # result 已经是 {"flow": ..., "refs": ...} 格式
    return result

# 确保静态目录存在
if not os.path.exists(settings.STATIC_DIR):
    print(f"Warning: Static directory {settings.STATIC_DIR} does not exist.")
else:
    # 挂载静态文件，html=True 表示访问 / 时自动查找 index.html
    app.mount("/", StaticFiles(directory=settings.STATIC_DIR, html=True), name="static")