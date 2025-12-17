from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.request import ResearchRequest
from app.service.chat_service import ChatService

router = APIRouter()
@router.post("/chat")
async def chat_endpoint(request: ResearchRequest):
    service = ChatService()
    return StreamingResponse(service.chat_stream(request.msg), media_type="application/x-ndjson")