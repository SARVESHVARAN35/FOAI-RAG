from pathlib import Path
import json

from app.rag.chunker import chunk_text
from app.rag.embeddings import generate_embeddings
from app.rag.vector_store import VectorStore


KNOWLEDGE_DIR = Path("knowledge")
VECTOR_STORE_DIR = Path("vector_store")

INDEX_PATH = VECTOR_STORE_DIR / "knowledge.index"
METADATA_PATH = VECTOR_STORE_DIR / "metadata.json"


def main():
    VECTOR_STORE_DIR.mkdir(exist_ok=True)

    # ---------------------------------------------------------
    # 1. Find knowledge files
    # ---------------------------------------------------------

    files = list(KNOWLEDGE_DIR.glob("*.md"))

    if not files:
        print("No Markdown knowledge files found.")
        return

    print(f"Found {len(files)} Markdown files.")

    all_chunks = []
    all_metadata = []

    # ---------------------------------------------------------
    # 2. Chunk every knowledge document
    # ---------------------------------------------------------

    for file_path in files:
        print(f"\nProcessing: {file_path.name}")

        text = file_path.read_text(encoding="utf-8")

        chunks = chunk_text(text)

        print(f"Chunks created: {len(chunks)}")

        for chunk_number, chunk in enumerate(chunks):
            all_chunks.append(chunk)

            all_metadata.append({
                "document": file_path.stem,
                "document_type": "KNOWLEDGE_DOCUMENT",
                "source_type": "document",
                "source_id": file_path.name,
                "chunk_number": chunk_number,
                "text": chunk
            })

    if not all_chunks:
        print("No chunks were created.")
        return

    # ---------------------------------------------------------
    # 3. Generate embeddings
    # ---------------------------------------------------------

    print(f"\nGenerating embeddings for {len(all_chunks)} chunks...")

    embeddings = generate_embeddings(all_chunks)

    # ---------------------------------------------------------
    # 4. Create a completely fresh FAISS index
    # ---------------------------------------------------------

    vector_store = VectorStore()

    vector_store.add_embeddings(embeddings)

    # ---------------------------------------------------------
    # 5. Save new index
    # ---------------------------------------------------------

    vector_store.save(str(INDEX_PATH))

    with open(METADATA_PATH, "w", encoding="utf-8") as file:
        json.dump(
            all_metadata,
            file,
            indent=2,
            ensure_ascii=False
        )

    # ---------------------------------------------------------
    # 6. Verification
    # ---------------------------------------------------------

    print("\n========== REBUILD COMPLETE ==========")
    print(f"Documents : {len(files)}")
    print(f"Chunks    : {len(all_chunks)}")
    print(f"Vectors   : {vector_store.index.ntotal}")
    print(f"Index     : {INDEX_PATH}")
    print(f"Metadata  : {METADATA_PATH}")
    print("=======================================")


if __name__ == "__main__":
    main()