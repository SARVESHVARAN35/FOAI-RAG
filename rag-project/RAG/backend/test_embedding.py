from app.rag.embeddings import generate_embedding

text = "My server gives 504 Gateway Timeout"

embedding = generate_embedding(text)

print("Embedding generated successfully")
print("Vector dimensions:", len(embedding))
print("First 5 values:", embedding[:5])