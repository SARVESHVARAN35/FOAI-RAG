from pathlib import Path
import json

from app.rag.chunker import chunk_text
from app.rag.embeddings import generate_embeddings
from app.rag.vector_store import VectorStore


INDEX_PATH = Path("vector_store/knowledge.index")
METADATA_PATH = Path("vector_store/metadata.json")


def ingest_approved_resolution(
    resolution_id: int,
    incident_title: str,
    error_code: str | None,
    service: str | None,
    root_cause: str,
    resolution_description: str,
    steps_taken: str,
    additional_notes: str | None
):
    # Build knowledge text from the actual approved resolution
    knowledge_text = f"""
# Approved Resolution

Incident Title: {incident_title}
Error Code: {error_code or "N/A"}
Service: {service or "N/A"}

## Root Cause

{root_cause}

## Resolution

{resolution_description}

## Steps Taken

{steps_taken}

## Additional Notes

{additional_notes or "N/A"}
""".strip()

    # Load existing metadata
    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        metadata = json.load(file)

    # Prevent duplicate indexing
    for item in metadata:
        if (
            item.get("source_type") == "resolution"
            and item.get("source_id") == resolution_id
        ):
            return {
                "status": "ALREADY_INDEXED",
                "resolution_id": resolution_id,
                "chunks_added": 0,
                "total_vectors": len(metadata)
            }

    # Chunk the approved resolution
    chunks = chunk_text(knowledge_text)

    if not chunks:
        raise ValueError(
            "No chunks were created from the approved resolution."
        )

    # Generate embeddings
    embeddings = generate_embeddings(chunks)

    # Load existing FAISS index
    vector_store = VectorStore()
    vector_store.load(str(INDEX_PATH))

    # Add embeddings
    vector_store.add_embeddings(embeddings)

    # Add metadata
    for chunk_number, chunk in enumerate(chunks):
        metadata.append({
            "document": f"approved-resolution-{resolution_id}",
            "document_type": "APPROVED_RESOLUTION",
            "source_type": "resolution",
            "source_id": resolution_id,
            "chunk_number": chunk_number,
            "text": chunk
        })

    # Save updated FAISS index
    vector_store.save(str(INDEX_PATH))

    # Save updated metadata
    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            metadata,
            file,
            indent=2,
            ensure_ascii=False
        )

    return {
        "status": "INDEXED",
        "resolution_id": resolution_id,
        "chunks_added": len(chunks),
        "total_vectors": vector_store.index.ntotal
    }