import traceback

from fastapi import APIRouter, HTTPException

from models.chat import ChatRequest, ChatResponse
from services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_repository(request: ChatRequest) -> ChatResponse:
    try:
        return chat_service.generate_answer(request)
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc!r}")
