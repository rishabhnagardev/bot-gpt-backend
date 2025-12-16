from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import SessionLocal
from app.models.user import User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(x_user_email: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    """Simple auth dependency that expects `X-User-Email` header.

    Returns the User model if it exists; raises 401 otherwise.
    """
    if not x_user_email:
        raise HTTPException(status_code=401, detail="Missing X-User-Email header")

    user = db.query(User).filter(User.email == x_user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Unknown user")

    return user
