import uvicorn
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.database.db import Database
from src.entrypoints.repos import repos_router

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await Database.initialize()
    yield
    await Database.close()

app = FastAPI(lifespan=lifespan)

app.include_router(repos_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)