from pathlib import Path
from app.rag.chunker import chunk_text


file_path = Path("knowledge/KB-001-504-gateway-timeout.md")

text = file_path.read_text(encoding="utf-8")

chunks = chunk_text(text)

print("Document:", file_path.name)
print("Number of chunks:", len(chunks))

for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i + 1} ---")
    print("Word count:", len(chunk.split()))
    print(chunk)