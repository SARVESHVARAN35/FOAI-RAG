import json
import logging
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field, field_validator

from app.core.security import require_roles
from app.schemas.auth import CurrentUser

logger = logging.getLogger(__name__)
router = APIRouter(tags=["rag"])
knowledge_router = APIRouter(tags=["knowledge"])

KNOWLEDGE_DIR = Path("knowledge")
INDEX_PATH = Path("vector_store/knowledge.index")
METADATA_PATH = Path("vector_store/metadata.json")


@knowledge_router.get("/knowledge")
def list_knowledge_documents(
    _admin: CurrentUser = Depends(require_roles("ADMIN"))
):
    try:
        with METADATA_PATH.open("r", encoding="utf-8") as metadata_file:
            metadata = json.load(metadata_file)

        if not isinstance(metadata, list):
            raise ValueError("Knowledge metadata must be a list.")

        document_chunks = {}
        for entry in metadata:
            if not isinstance(entry, dict):
                raise ValueError("Knowledge metadata entries must be objects.")

            document_name = entry.get("document")
            if isinstance(document_name, str) and document_name:
                document_chunks[document_name] = (
                    document_chunks.get(document_name, 0) + 1
                )

        return {
            "documents": [
                {"document": document_name, "chunks": chunk_count}
                for document_name, chunk_count in document_chunks.items()
            ]
        }
    except Exception as exc:
        logger.exception("Unexpected error while listing knowledge documents.")
        raise HTTPException(
            status_code=500,
            detail="Knowledge documents could not be loaded. Please try again later.",
        ) from exc


class RAGQueryRequest(BaseModel):
    query: str = Field(min_length=1)

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, query: str) -> str:
        if not query.strip():
            raise ValueError("Query must not be empty.")
        return query


@router.post("/query")
def query_rag(
    request: Request,
    body: RAGQueryRequest,
    _user: CurrentUser = Depends(
        require_roles("SUPPORT_ENGINEER", "IT_LEAD", "ADMIN")
    ),
):
    try:
        return request.app.state.rag_pipeline.query(body.query)
    except Exception as exc:
        logger.exception("Unexpected error while processing a RAG query.")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the query.",
        ) from exc


@knowledge_router.post("/knowledge/pdf")
async def upload_knowledge_pdf(
    file: UploadFile = File(...),
    _admin: CurrentUser = Depends(require_roles("ADMIN")),
):
    filename = (file.filename or "").replace("\\", "/")
    document_name = Path(filename).name

    if not document_name or Path(document_name).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    try:
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

        with METADATA_PATH.open("r", encoding="utf-8") as metadata_file:
            metadata = json.load(metadata_file)

        if not isinstance(metadata, list):
            raise ValueError("Knowledge metadata must be a list.")

        if any(
            isinstance(entry, dict) and entry.get("document") == document_name
            for entry in metadata
        ):
            from app.rag.vector_store import VectorStore

            vector_store = VectorStore()
            vector_store.load(str(INDEX_PATH))
            return {
                "status": "ALREADY_EXISTS",
                "message": "This PDF is already indexed.",
                "document": document_name,
                "pages": None,
                "chunks_added": 0,
                "total_vectors": vector_store.index.ntotal,
                "total_metadata": len(metadata),
            }

        saved_pdf_path = KNOWLEDGE_DIR / document_name

        with saved_pdf_path.open("wb") as destination:
            shutil.copyfileobj(file.file, destination)

        from app.rag.pdf_ingestion import ingest_pdf

        result = ingest_pdf(str(saved_pdf_path))
        return {
            "status": "SUCCESS",
            "message": "PDF uploaded and indexed successfully.",
            **result,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error while uploading a knowledge PDF.")
        raise HTTPException(
            status_code=500,
            detail="The PDF could not be processed. Please verify the file and try again.",
        ) from exc
