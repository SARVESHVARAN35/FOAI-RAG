from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker:

    def __init__(self):
        print("Loading cross-encoder model...")

        self.model = CrossEncoder(
            MODEL_NAME
        )

        print("Cross-encoder loaded.")

    def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int = 3
    ):
        if not documents:
            return []

        # Create query-document pairs
        pairs = [
            [query, document]
            for document in documents
        ]

        # Generate relevance scores
        scores = self.model.predict(
            pairs
        )

        # Combine documents with scores
        results = []

        for document, score in zip(
            documents,
            scores
        ):
            results.append({
                "document": document,
                "score": float(score)
            })

        # Highest score = most relevant
        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results[:top_k]