import uvicorn
import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from src.database.db import Database
from src.entrypoints.repos import repos_router
from src.domain.error_handlers import validation_exception_handler

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):   # инициализация БД до начала запросов и закрытие соедениия после
    await Database.initialize()
    yield
    await Database.close()

app = FastAPI(lifespan=lifespan)

app.include_router(repos_router, prefix="/api")
app.add_exception_handler(RequestValidationError, validation_exception_handler)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)