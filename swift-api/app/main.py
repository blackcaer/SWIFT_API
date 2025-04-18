from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_db_and_tables
from app.routers import messages, swift_codes


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(messages.router)
app.include_router(swift_codes.router)


@app.get("/")
def read_root():
    return {"message": "Hello World with FastAPI and PostgreSQL!"}
