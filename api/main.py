from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from core.exceptions import custom_http_exception_handler, validation_exception_handler
from core.config import settings
from db.database import async_session_maker, create_db_and_tables, engine
from routers.auth import router as auth_router
from routers.collection import router as collection_router
from routers.items import router as items_router
from routers.stats import router as stats_router
from seed import seed_items


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    async with async_session_maker() as session:
        await seed_items(session)
    yield
    await engine.dispose()


app = FastAPI(title="Ma Collection API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(StarletteHTTPException, custom_http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(auth_router)
app.include_router(collection_router)
app.include_router(items_router)
app.include_router(stats_router)


@app.get("/")
async def root():
    return {"message": "Ma Collection API"}


@app.get("/health")
async def health_check():
    async with async_session_maker() as session:
        await session.execute(text("SELECT 1"))
    return {"status": "ok"}
