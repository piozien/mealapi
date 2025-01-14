"""Main module of the app"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request, Response

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


app = FastAPI(
    title="MealAPI",
    description="""
    🍳 MealAPI - Kompleksowe API do zarządzania przepisami kulinarnymi

    ## Funkcjonalności

    * 👩‍🍳 **Przepisy** - tworzenie, edycja, usuwanie i wyszukiwanie przepisów
    * 🌟 **Oceny** - ocenianie przepisów i wyświetlanie średnich ocen
    * 💬 **Komentarze** - dodawanie i zarządzanie komentarzami do przepisów
    * 🔍 **Wyszukiwanie** - zaawansowane wyszukiwanie przepisów po różnych kryteriach
    * 🏷️ **Tagi** - kategoryzacja przepisów za pomocą tagów
    * 🤖 **AI Detection** - wykrywanie przepisów generowanych przez AI

    ## Autoryzacja

    API używa JWT (JSON Web Tokens) do autoryzacji. Aby uzyskać dostęp do chronionych endpointów:
    1. Zarejestruj się używając endpointu `/register`
    2. Zaloguj się używając endpointu `/login`
    3. Użyj otrzymanego tokenu w nagłówku `Authorization: Bearer <token>`

    ## Role użytkowników

    * **USER** - podstawowy dostęp (dodawanie przepisów, komentowanie)
    * **ADMIN** - pełny dostęp (moderacja, usuwanie treści)
    """,
    openapi_tags=[
        {
            "name": "recipe",
            "description": "Operacje związane z przepisami kulinarnymi",
        },
        {
            "name": "comment",
            "description": "Zarządzanie komentarzami do przepisów",
        },
        {
            "name": "report",
            "description": "System zgłaszania nieodpowiednich treści",
        },
        {
            "name": "user",
            "description": "Zarządzanie użytkownikami i autoryzacja",
        },
    ],
    lifespan=lifespan
)

app.include_router(recipe_router, prefix="/recipe")
app.include_router(comment_router, prefix="/comment")
app.include_router(report_router, prefix="/report")
app.include_router(user_router, prefix="")


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exception: HTTPException,
) -> Response:
    return Response(
        content=exception.detail,
        status_code=exception.status_code,
    )
