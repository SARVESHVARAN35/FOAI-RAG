import faiss
import numpy as np


EMBEDDING_DIMENSION = 384


class VectorStore:
    def __init__(self):
        # Inner Product on normalized vectors = Cosine Similarity
        self.index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)

    def add_embeddings(self, embeddings):
        vectors = np.array(embeddings).astype("float32")

        # Normalize vectors so Inner Product becomes Cosine Similarity
        faiss.normalize_L2(vectors)

        self.index.add(vectors)

    def search(self, query_embedding, top_k=3):
        query_vector = np.array(
            [query_embedding],
            dtype="float32"
        )

        # Normalize query vector
        faiss.normalize_L2(query_vector)

        # Higher score = more similar
        similarities, indices = self.index.search(
            query_vector,
            top_k
        )

        return similarities[0], indices[0]

    def save(self, path):
        faiss.write_index(self.index, path)

    def load(self, path):
        self.index = faiss.read_index(path)