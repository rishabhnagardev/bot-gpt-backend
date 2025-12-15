from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.message import MessageCreate, MessageResponse
from app.services.message_service import process_user_message

router = APIRouter(
    prefix="/conversations/{conversation_id}/messages",
    tags=["Messages"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=MessageResponse)
def add_message(
    conversation_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db)
):
    assistant_msg = process_user_message(
        db, conversation_id, data.content
    )

    if not assistant_msg:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return assistant_msg
