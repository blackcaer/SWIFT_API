from fastapi import APIRouter
from sqlmodel import Session, select
from app.models import Message
from app.database import engine

router = APIRouter()


@router.post("/messages/")
def create_message(content: str):
    message = Message(content=content)
    with Session(engine) as session:
        session.add(message)
        session.commit()
        session.refresh(message)
    return message


@router.get("/messages/")
def read_messages():
    with Session(engine) as session:
        messages = session.exec(select(Message)).all()
    return messages
