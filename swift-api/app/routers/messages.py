from fastapi import APIRouter, HTTPException
from sqlmodel import select, Session
from app.models import Message
from app.database import SessionDep

router = APIRouter(prefix="/messages")

@router.post("/")
def create_message(content: str, db: SessionDep):
    message = Message(content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

@router.get("/")
def read_messages(db: SessionDep):
    messages = db.exec(select(Message)).all()
    return messages