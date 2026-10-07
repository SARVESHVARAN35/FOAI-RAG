from pathlib import Path
import json

from pypdf import PdfReader

from app.rag.chunker import chunk_text, split_large_section
from app.rag.embeddings import generate_embeddings
from app.rag.vector_store import VectorStore


INDEX_PATH = Path("vector_store/knowledge.index")
METADATA_PATH = Path("vector_store/metadata.json")


def ingest_pdf(pdf_path: str):
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    # ---------------------------------------------------------
    # 1. Load existing metadata
    # ---------------------------------------------------------

    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        metadata = json.load(file)

    # ---------------------------------------------------------
    # 2. Prevent duplicate ingestion
    # ---------------------------------------------------------

    for item in metadata:
        if (
            item.get("source_type") == "pdf"
            and item.get("source_id") == pdf_path.name
        ):
            return {
                "status": "ALREADY_INDEXED",
                "document": pdf_path.name,
                "chunks_added": 0,
                "total_vectors": len(metadata)
            }

    # ---------------------------------------------------------
    # 3. Extract PDF text
    # ---------------------------------------------------------

    reader = PdfReader(str(pdf_path))

    all_text = []

    for page in reader.pages:
        text = page.extract_text() or ""

        if text.strip():
            all_text.append(text)

    full_text = "\n".join(all_text)

    if not full_text.strip():
        raise ValueError(
            f"No text could be extracted from {pdf_path.name}"
        )

    print(f"PDF: {pdf_path.name}")
    print(f"Pages: {len(reader.pages)}")
    print(f"Extracted characters: {len(full_text)}")

    # ---------------------------------------------------------
    # 4. Try structure-aware chunking
    # ---------------------------------------------------------

    chunks = chunk_text(full_text)

    # ---------------------------------------------------------
    # 5. PDF fallback
    #
    # PDFs may not contain Markdown headings.
    # In that case, use direct 500 / 100 splitting.
    # ---------------------------------------------------------

    if not chunks:
        print("No structured sections found.")
        print("Using 500-word / 100-word overlap fallback.")

        chunks = split_large_section(
            full_text,
            max_words=500,
            overlap=100
        )

    if not chunks:
        raise ValueError(
            f"No chunks were created from {pdf_path.name}"
        )

    print(f"Chunks created: {len(chunks)}")

    # ---------------------------------------------------------
    # 6. Generate embeddings
    # ---------------------------------------------------------

    print("Generating embeddings...")

    embeddings = generate_embeddings(chunks)

    # ---------------------------------------------------------
    # 7. Load existing FAISS index
    # ---------------------------------------------------------

    vector_store = VectorStore()

    vector_store.load(
        str(INDEX_PATH)
    )

    # ---------------------------------------------------------
    # 8. Add PDF embeddings
    # ---------------------------------------------------------

    vector_store.add_embeddings(
        embeddings
    )

    # ---------------------------------------------------------
    # 9. Add metadata
    # ---------------------------------------------------------

    for chunk_number, chunk in enumerate(chunks):

        metadata.append({
            "document": pdf_path.name,
            "document_type": "PDF",
            "source_type": "pdf",
            "source_id": pdf_path.name,
            "chunk_number": chunk_number,
            "text": chunk
        })

    # ---------------------------------------------------------
    # 10. Save FAISS index
    # ---------------------------------------------------------

    vector_store.save(
        str(INDEX_PATH)
    )

    # ---------------------------------------------------------
    # 11. Save metadata
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # 12. Return result
    # ---------------------------------------------------------

    return {
        "status": "INDEXED",
        "document": pdf_path.name,
        "pages": len(reader.pages),
        "chunks_added": len(chunks),
        "total_vectors": vector_store.index.ntotal,
        "total_metadata": len(metadata)
    }
