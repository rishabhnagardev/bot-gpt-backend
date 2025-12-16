from sqlalchemy.orm import Session
import logging

from app.models.user import User
from app.models.conversation import Conversation
from app.db import cache

logger = logging.getLogger(__name__)


def get_or_create_user(db: Session, email: str) -> User:
    """Return an existing User or create one.

    Minimal helper used by `create_conversation`.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Created new user %s", email)
    return user


def create_conversation(db: Session, user_email: str, mode: str, title: str = None):
    """Create a conversation and cache it."""
    user = get_or_create_user(db, user_email)

    conversation = Conversation(
        user_id=user.id,
        mode=mode,
        title=title
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    cache.set_conversation(conversation.id, conversation)
    logger.info("Created conversation %s for user %s", conversation.id, user_email)
    return conversation


def list_conversations(db: Session, user_email: str, limit: int, offset: int):
    """Return a paginated list of conversations for a user."""
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
    """Get a conversation; use cache if available."""
    cached = cache.get_conversation(conversation_id)
    if cached:
        logger.info("Cache hit for conversation %s", conversation_id)
        return cached

    convo = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if convo:
        cache.set_conversation(convo.id, convo)
    return convo


def delete_conversation(db: Session, conversation_id: int):
    convo = get_conversation(db, conversation_id)
    if convo:
        db.delete(convo)
        db.commit()
        cache.invalidate_conversation(conversation_id)
        logger.info("Deleted conversation %s", conversation_id)
    return convo
