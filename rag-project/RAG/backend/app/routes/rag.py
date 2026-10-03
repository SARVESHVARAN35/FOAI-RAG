import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)
router = APIRouter(tags=["rag"])


class RAGQueryRequest(BaseModel):
    query: str = Field(min_length=1)

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, query: str) -> str:
        if not query.strip():
            raise ValueError("Query must not be empty.")
        return query


@router.post("/query")
def query_rag(request: Request, body: RAGQueryRequest):
    try:
        return request.app.state.rag_pipeline.query(body.query)
    except Exception as exc:
        logger.exception("Unexpected error while processing a RAG query.")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the query.",
        ) from exc
