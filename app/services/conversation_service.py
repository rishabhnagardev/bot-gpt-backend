from sqlalchemy.orm import Session

from app.models.user import User
from app.models.conversation import Conversation


def get_or_create_user(db: Session, email: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def create_conversation(db: Session, user_email: str, mode: str, title: str = None):
    user = get_or_create_user(db, user_email)

    conversation = Conversation(
        user_id=user.id,
        mode=mode,
        title=title
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def list_conversations(db: Session, user_email: str, limit: int, offset: int):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return []

    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_conversation(db: Session, conversation_id: int):
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def delete_conversation(db: Session, conversation_id: int):
    convo = get_conversation(db, conversation_id)
    if convo:
        db.delete(convo)
        db.commit()
    return convo
