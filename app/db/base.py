from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import models so SQLAlchemy knows them
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.document import Document
from app.models.conversation_document import ConversationDocument