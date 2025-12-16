import logging
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.base import Base
from app.db.session import engine

from app.api import conversations, messages


# Create tables (models will be added later)
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="BOT GPT Backend",
    description="Conversational AI backend for BOT Consulting",
    version="0.1.0"
)

app.include_router(conversations.router)
app.include_router(messages.router)

# Configure simple logging for the application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    return {
        "status": "ok",
        "database": "connected"
    }
