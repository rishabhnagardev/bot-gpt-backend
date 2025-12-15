from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import SessionLocal
from app.schemas.conversation import ConversationCreate, ConversationResponse
from app.services.conversation_service import (
    create_conversation,
    list_conversations,
    get_conversation,
    delete_conversation
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=ConversationResponse)
def create(data: ConversationCreate, db: Session = Depends(get_db)):
    return create_conversation(db, data.user_email, data.mode, data.title)


@router.get("", response_model=List[ConversationResponse])
def list_all(
    user_email: str,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    return list_conversations(db, user_email, limit, offset)


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_one(conversation_id: int, db: Session = Depends(get_db)):
    convo = get_conversation(db, conversation_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return convo


@router.delete("/{conversation_id}")
def delete_one(conversation_id: int, db: Session = Depends(get_db)):
    convo = delete_conversation(db, conversation_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted"}
