from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConversationCreate(BaseModel):
    user_email: str
    mode: str = "open"
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    id: int
    mode: str
    title: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
