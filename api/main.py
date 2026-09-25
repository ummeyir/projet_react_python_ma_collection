from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from core.exceptions import custom_http_exception_handler, validation_exception_handler
from routers.auth import router as auth_router
from routers.collection import router as collection_router
from routers.items import router as items_router
from routers.stats import router as stats_router

app = FastAPI(title="Ma Collection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
    return {"status": "ok"}
