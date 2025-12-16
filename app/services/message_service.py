from sqlalchemy.orm import Session

from app.models.message import Message
from app.models.conversation import Conversation
from app.services.llm_service import call_llm
from app.services.summarization_service import summarize_messages

MAX_RAW_MESSAGES = 10 # configurable: number of recent messages to keep in raw form before summarizing

def add_user_message(db: Session, conversation_id: int, content: str) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        role="user",
        content=content
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def add_assistant_message(db: Session, conversation_id: int, content: str) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=content
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def process_user_message(db, conversation_id, user_content):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        return None

    add_user_message(db, conversation_id, user_content)

    messages = conversation.messages

    if len(messages) > MAX_RAW_MESSAGES:
        old_msgs = messages[:-MAX_RAW_MESSAGES]
        summary = summarize_messages(old_msgs)
        conversation.summary = summary
        db.commit()

        recent_messages = messages[-MAX_RAW_MESSAGES:]
    else:
        recent_messages = messages

    assistant_reply = call_llm(
        recent_messages, user_content
    )

    return add_assistant_message(
        db, conversation_id, assistant_reply
    )
