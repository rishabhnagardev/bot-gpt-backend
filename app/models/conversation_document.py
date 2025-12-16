from sqlalchemy import Column, Integer, ForeignKey
from app.db.base import Base


class ConversationDocument(Base):
    __tablename__ = "conversation_documents"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE")
    )
    document_id = Column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE")
    )
