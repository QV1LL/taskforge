import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

# Налаштовуємо логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskforge")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код ініціалізації ресурсів
    logger.info("Initializing TaskForge resources (Database pools, Cache)...")
    yield
    # Код очищення ресурсів
    logger.info("Releasing TaskForge resources...")


app = FastAPI(
    title="TaskForge API",
    description="Система управління проєктами та завданнями",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"status": "ok", "project": "TaskForge", "version": "0.1.0"}
