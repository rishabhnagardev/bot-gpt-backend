from sqlalchemy.orm import Session

from app.models.message import Message
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.conversation_document import ConversationDocument
from app.services.llm_service import call_llm
from app.services.summarization_service import summarize_messages
from app.services.rag_service import retrieve_relevant_chunks

MAX_RAW_MESSAGES = 10


def add_user_message(
    db: Session,
    conversation_id: int,
    content: str
) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        role="user",
        content=content
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def add_assistant_message(
    db: Session,
    conversation_id: int,
    content: str
) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=content
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def process_user_message(
    db: Session,
    conversation_id: int,
    user_content: str
):
    # 1. Fetch conversation
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if not conversation:
        return None

    # 2. Store user message
    add_user_message(db, conversation_id, user_content)

    db.refresh(conversation)
    messages = conversation.messages

    # 3. Summary-based context trimming
    if len(messages) > MAX_RAW_MESSAGES:
        old_messages = messages[:-MAX_RAW_MESSAGES]

        summary = summarize_messages(old_messages)
        conversation.summary = summary
        db.commit()

        recent_messages = messages[-MAX_RAW_MESSAGES:]
    else:
        recent_messages = messages

    # 4. Retrieve RAG context (conversation-scoped)
    context_chunks = None
    if conversation.mode == "rag":
        document_ids = (
            db.query(ConversationDocument.document_id)
            .filter(
                ConversationDocument.conversation_id == conversation_id
            )
            .all()
        )

        document_ids = [d[0] for d in document_ids]

        if document_ids:
            documents = (
                db.query(Document)
                .filter(Document.id.in_(document_ids))
                .all()
            )

            context_chunks = retrieve_relevant_chunks(
                documents,
                user_content,
                top_k=2
            )

    # 5. LLM call (open or rag)
    assistant_reply = call_llm(
        conversation=conversation,
        recent_messages=recent_messages,
        user_message=user_content,
        context_chunks=context_chunks
    )

    # 6. Store assistant response
    return add_assistant_message(
        db,
        conversation_id,
        assistant_reply
    )
