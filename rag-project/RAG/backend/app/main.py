import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health
from app.core.config import settings
from app.routes.rag import knowledge_router, router as rag_router
from app.routes.auth import router as auth_router
from app.routes.incident import router as incidents_router
from app.routes.resolutions import router as resolutions_router
from app.routes.reviews import router as reviews_router

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

@asynccontextmanager
async def lifespan(application: FastAPI):
    from app.rag.pipeline import RAGPipeline

    application.state.rag_pipeline = RAGPipeline()
    yield


app = FastAPI(
    title="Enterprise IT Incident Knowledge RAG Assistant",
    description=(
        "A RAG-based API for troubleshooting enterprise IT incidents "
        "using approved knowledge documents."
    ),
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth_router)
app.include_router(rag_router, prefix="/rag")
app.include_router(knowledge_router)
app.include_router(incidents_router)
app.include_router(resolutions_router)
app.include_router(reviews_router)

@app.get("/")
def root():
    return {
        "message": (
            "Enterprise IT Incident Knowledge RAG Assistant API is running."
        )
    }