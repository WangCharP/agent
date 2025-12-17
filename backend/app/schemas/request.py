from pydantic import BaseModel

class ChatRequest(BaseModel):
    msg: str
    type: str = "text"
