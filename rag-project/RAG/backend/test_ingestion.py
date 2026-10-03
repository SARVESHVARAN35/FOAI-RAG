from pathlib import Path
import json

from app.rag.chunker import chunk_text
from app.rag.embeddings import generate_embeddings
from app.rag.vector_store import VectorStore


# --------------------------------------------------
# 1. Locate knowledge documents
# --------------------------------------------------

knowledge_dir = Path("knowledge")

knowledge_files = sorted(
    knowledge_dir.glob("*.md")
)

print("Knowledge documents found:", len(knowledge_files))

for file in knowledge_files:
    print(" -", file.name)


# --------------------------------------------------
# 2. Read and chunk all knowledge documents
# --------------------------------------------------

all_chunks = []
metadata = []

for file_path in knowledge_files:

    print("\n" + "=" * 70)
    print("Processing:", file_path.name)
    print("=" * 70)

    # Read document
    text = file_path.read_text(
        encoding="utf-8"
    )

    # Create chunks
    chunks = chunk_text(text)

    print("Chunks created:", len(chunks))

    # Store chunks and metadata
    for chunk_number, chunk in enumerate(chunks):

        all_chunks.append(chunk)

        metadata.append({
            "document": file_path.name,
            "chunk_number": chunk_number,
            "text": chunk
        })


# --------------------------------------------------
# 3. Generate embeddings
# --------------------------------------------------

print("\n" + "=" * 70)
print("Generating embeddings")
print("=" * 70)

embeddings = generate_embeddings(
    all_chunks
)

print(
    "Total chunks:",
    len(all_chunks)
)

print(
    "Total embeddings:",
    len(embeddings)
)

print(
    "Embedding dimension:",
    len(embeddings[0])
)


# --------------------------------------------------
# 4. Create FAISS cosine similarity index
# --------------------------------------------------

print("\n" + "=" * 70)
print("Creating FAISS cosine similarity index")
print("=" * 70)

store = VectorStore()

# VectorStore handles:
# - float32 conversion
# - L2 normalization
# - FAISS IndexFlatIP
#
# Normalized Inner Product = Cosine Similarity

store.add_embeddings(
    embeddings
)

print(
    "Vectors stored in FAISS:",
    store.index.ntotal
)


# --------------------------------------------------
# 5. Create vector_store directory
# --------------------------------------------------

vector_store_dir = Path(
    "vector_store"
)

vector_store_dir.mkdir(
    exist_ok=True
)


# --------------------------------------------------
# 6. Save FAISS index
# --------------------------------------------------

index_path = (
    vector_store_dir /
    "knowledge.index"
)

store.save(
    str(index_path)
)

print(
    "FAISS cosine similarity index saved to:",
    index_path
)


# --------------------------------------------------
# 7. Save metadata
# --------------------------------------------------

metadata_path = (
    vector_store_dir /
    "metadata.json"
)

with open(
    metadata_path,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        metadata,
        file,
        indent=4,
        ensure_ascii=False
    )


print(
    "Metadata saved to:",
    metadata_path
)


# --------------------------------------------------
# 8. Final verification
# --------------------------------------------------

print("\n" + "=" * 70)
print("INGESTION COMPLETED")
print("=" * 70)

print(
    "Documents:",
    len(knowledge_files)
)

print(
    "Total chunks:",
    len(all_chunks)
)

print(
    "Total vectors:",
    store.index.ntotal
)

print(
    "Vector dimension:",
    len(embeddings[0])
)

print(
    "Similarity metric:",
    "Cosine Similarity"
)

print(
    "Index type:",
    type(store.index).__name__
)

print(
    "Metadata includes chunk text:",
    "Yes"
)

print("=" * 70)