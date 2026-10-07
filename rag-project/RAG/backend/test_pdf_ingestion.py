from pathlib import Path
import json

from pypdf import PdfReader

from app.rag.chunker import chunk_text
from app.rag.embeddings import generate_embeddings
from app.rag.vector_store import VectorStore


# --------------------------------------------------
# Paths
# --------------------------------------------------

PDF_PATH = Path("knowledge/aws-security-incident-response-guide.pdf")
INDEX_PATH = Path("vector_store/knowledge.index")
METADATA_PATH = Path("vector_store/metadata.json")


# --------------------------------------------------
# 1. Extract PDF text
# --------------------------------------------------

print("Reading PDF...")

reader = PdfReader(str(PDF_PATH))

all_text = []

for page in reader.pages:
    text = page.extract_text() or ""
    all_text.append(text)

full_text = "\n".join(all_text)

print("Pages:", len(reader.pages))
print("Characters:", len(full_text))
print("Words:", len(full_text.split()))


# --------------------------------------------------
# 2. Chunk PDF text
# --------------------------------------------------

print("\nChunking PDF...")

chunks = chunk_text(full_text)

print("PDF chunks:", len(chunks))


# --------------------------------------------------
# 3. Generate embeddings
# --------------------------------------------------

print("\nGenerating embeddings...")

embeddings = generate_embeddings(chunks)

print("Embeddings:", len(embeddings))


# --------------------------------------------------
# 4. Load existing FAISS index
# --------------------------------------------------

print("\nLoading existing FAISS index...")

vector_store = VectorStore()
vector_store.load(str(INDEX_PATH))

print("Existing vectors:", vector_store.index.ntotal)


# --------------------------------------------------
# 5. Add PDF embeddings
# --------------------------------------------------

vector_store.add_embeddings(embeddings)

print("Vectors after PDF:", vector_store.index.ntotal)


# --------------------------------------------------
# 6. Load existing metadata
# --------------------------------------------------

with open(METADATA_PATH, "r", encoding="utf-8") as file:
    metadata = json.load(file)


# --------------------------------------------------
# 7. Add PDF metadata
# --------------------------------------------------

for chunk_number, chunk in enumerate(chunks):
    metadata.append({
        "document": PDF_PATH.name,
        "chunk_number": chunk_number,
        "text": chunk
    })


# --------------------------------------------------
# 8. Save updated FAISS index
# --------------------------------------------------

vector_store.save(str(INDEX_PATH))


# --------------------------------------------------
# 9. Save updated metadata
# --------------------------------------------------

with open(METADATA_PATH, "w", encoding="utf-8") as file:
    json.dump(metadata, file, indent=2, ensure_ascii=False)


print("\n" + "=" * 60)
print("PDF INGESTION COMPLETE")
print("=" * 60)

print("PDF:", PDF_PATH.name)
print("PDF chunks added:", len(chunks))
print("Total FAISS vectors:", vector_store.index.ntotal)
print("Total metadata entries:", len(metadata))