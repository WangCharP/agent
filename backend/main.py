import uvicorn
import os
import sys

from app.config import settings

# 在 python 路径中加入后端路径和项目根目录（以支持 kg_agent 包导入）
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(backend_dir, '..'))
sys.path.insert(0, backend_dir)
sys.path.insert(0, project_root)

if __name__ == "__main__":
    uvicorn.run(
        "app.api.routes:app",
        host = settings.HOST,
        port = settings.PORT,
        reload = True
    )


