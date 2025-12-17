import uvicorn
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- 🔥 关键修复：添加父目录到搜索路径 ---
# 获取当前文件 (main.py) 的目录 -> backend
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取 backend 的父目录 -> project_root
parent_dir = os.path.dirname(current_dir)
# 将 project_root 加入 Python 搜索路径，这样就能找到 kg_agent 了
sys.path.insert(0, parent_dir)
# ---------------------------------------

# 注意：必须在修改 sys.path 之后再导入 app 模块
from app.config import settings
from app.api.routes import router as api_router

app = FastAPI(title="Multi-Agent Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    print(f"Server is running on http://{settings.HOST}:{settings.PORT}")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)