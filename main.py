from information import information
from fastapi import FastAPI
from contextlib import asynccontextmanager
from resources.routes import api_router
import database_definition


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database_definition.database.connect()
    yield
    await database_definition.database.disconnect()


information.update({"lifespan": lifespan})
app = FastAPI(**information)
app.include_router(api_router)
