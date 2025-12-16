from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.conversation_document import ConversationDocument
from app.schemas.message import MessageResponse
from app.services.message_service import process_user_message
from app.services.pdf_service import extract_text_from_pdf

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
    content: str = Form(...),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if not conversation:
        raise HTTPException(404, "Conversation not found")

    # Handle PDF upload inline (RAG only)
    if file:
        if conversation.mode != "rag":
            raise HTTPException(
                400, "PDF upload allowed only in RAG mode"
            )

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

    assistant_msg = process_user_message(
        db, conversation_id, content
    )

    return assistant_msg
