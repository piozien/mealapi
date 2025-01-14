"""Main module of the app"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI


from mealapi.api.routers.recipe import router as recipe_router
from mealapi.api.routers.comment import router as comment_router
from mealapi.api.routers.report import router as report_router
from mealapi.api.routers.user import router as user_router
from mealapi.container import Container
from mealapi.db import database, init_db

container = Container()

container.wire(modules=[
    "mealapi.api.routers.recipe",
    "mealapi.api.routers.comment",
    "mealapi.api.routers.report",
    "mealapi.api.routers.user",
])


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:
    await init_db()
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(recipe_router, prefix="/recipe")
app.include_router(comment_router, prefix="/comment")
app.include_router(report_router, prefix="/report")
app.include_router(user_router, prefix="")


