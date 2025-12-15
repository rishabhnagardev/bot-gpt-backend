from sqlalchemy.orm import Session

from app.models.message import Message
from app.models.conversation import Conversation
from app.services.llm_service import call_llm


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


def process_user_message(db: Session, conversation_id: int, user_content: str):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        return None

    # 1️⃣ Save user message
    user_msg = add_user_message(db, conversation_id, user_content)

    # 2️⃣ Fetch history
    history = conversation.messages

    # 3️⃣ Call LLM
    assistant_reply = call_llm(history, user_content)

    # 4️⃣ Save assistant reply
    assistant_msg = add_assistant_message(
        db, conversation_id, assistant_reply
    )

    return assistant_msg
