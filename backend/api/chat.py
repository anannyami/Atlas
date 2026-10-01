import logging

from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool

from models.chat import ChatRequest, ChatResponse
from services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
async def chat_with_repository(request: ChatRequest) -> ChatResponse:
    try:
        return await run_in_threadpool(chat_service.generate_answer, request)
    except Exception as exc:
        logger.exception("Chat request failed")
        raise HTTPException(status_code=500, detail="Chat request failed.") from exc
