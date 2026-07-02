import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import projects, tasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskforge")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing TaskForge resources...")
    yield
    logger.info("Releasing TaskForge resources...")


app = FastAPI(
    title="TaskForge API",
    description="Система управління проєктами та завданнями",
    version="0.1.0",
    lifespan=lifespan,
)

# Підключаємо модулі маршрутів
app.include_router(projects.router)
app.include_router(tasks.router)


@app.get("/")
async def root():
    return {"status": "ok", "project": "TaskForge", "version": "0.1.0"}
