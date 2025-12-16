from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import logging

from app.api.deps import get_db, get_current_user
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.conversation_document import ConversationDocument
from app.schemas.message import MessageResponse
from app.services.message_service import process_user_message
from app.services.pdf_service import extract_text_from_pdf

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/conversations/{conversation_id}/messages",
    tags=["Messages"]
)


@router.post("", response_model=MessageResponse)
async def add_message(
    conversation_id: int,
    content: str = Form(...),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Accept a user message (and optional PDF). Ensures the authenticated
    user owns the conversation. This endpoint delegates core work to
    `process_user_message` which is async to allow non-blocking LLM calls.
    """
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if not conversation:
        raise HTTPException(404, "Conversation not found")

    if conversation.user_id != current_user.id:
        raise HTTPException(403, "Forbidden")

    # Handle PDF upload inline (RAG only)
    if file:
        if conversation.mode != "rag":
            raise HTTPException(400, "PDF upload allowed only in RAG mode")

        if not file.filename.endswith(".pdf"):
            raise HTTPException(400, "Only PDF files supported")

        text = extract_text_from_pdf(file.file)

        if not text:
            raise HTTPException(400, "Could not extract text from PDF")

        document = Document(
            filename=file.filename,
            content=text
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        link = ConversationDocument(
            conversation_id=conversation_id,
            document_id=document.id
        )
        db.add(link)
        db.commit()
        logger.info("Stored PDF %s for conversation %s", document.filename, conversation_id)

    assistant_msg = await process_user_message(db, conversation_id, content)

    return assistant_msg
