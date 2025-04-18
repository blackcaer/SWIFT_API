from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import messages

app = FastAPI()


from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)


app.include_router(messages.router)


@app.get("/")
def read_root():
    return {"message": "Hello World with FastAPI and PostgreSQL!"}
