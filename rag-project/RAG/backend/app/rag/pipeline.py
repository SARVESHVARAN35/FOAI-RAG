from pathlib import Path
import json

from app.rag.embeddings import generate_embedding
from app.rag.vector_store import VectorStore
from app.rag.reranker import Reranker
from app.rag.generator import Generator


class RAGPipeline:

    RELEVANCE_THRESHOLD = 1.0

    def __init__(self):

        # ----------------------------------------------------
        # Paths
        # ----------------------------------------------------

        self.vector_store_path = Path(
            "vector_store/knowledge.index"
        )

        self.metadata_path = Path(
            "vector_store/metadata.json"
        )


        # ----------------------------------------------------
        # Load FAISS
        # ----------------------------------------------------

        self.vector_store = VectorStore()

        self.vector_store.load(
            str(self.vector_store_path)
        )


        # ----------------------------------------------------
        # Load metadata
        # ----------------------------------------------------

        with open(
            self.metadata_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.metadata = json.load(file)


        # ----------------------------------------------------
        # Load models
        # ----------------------------------------------------

        self.reranker = Reranker()

        self.generator = Generator()


    def query(
        self,
        user_query: str,
        retrieval_k: int = 5,
        final_k: int = 3
    ):

        # ====================================================
        # STEP 1: CREATE QUERY EMBEDDING
        # ====================================================

        query_embedding = generate_embedding(
            user_query
        )


        # ====================================================
        # STEP 2: FAISS RETRIEVAL
        # ====================================================

        similarities, indices = self.vector_store.search(
            query_embedding,
            top_k=retrieval_k
        )


        candidates = []


        for similarity, index in zip(
            similarities,
            indices
        ):

            if index == -1:
                continue


            document_info = self.metadata[index]


            candidates.append({

                "faiss_similarity": float(
                    similarity
                ),

                "document": document_info[
                    "document"
                ],

                "chunk_number": document_info[
                    "chunk_number"
                ],

                "text": document_info[
                    "text"
                ]

            })


        # ====================================================
        # STEP 3: CROSS-ENCODER RERANKING
        # ====================================================

        candidate_texts = [

            candidate["text"]

            for candidate in candidates

        ]


        reranked_results = self.reranker.rerank(

            query=user_query,

            documents=candidate_texts,

            top_k=final_k

        )


        # ====================================================
        # STEP 4: CHECK RESULTS
        # ====================================================

        if not reranked_results:

            return {

                "status": "REJECTED",

                "answer": (
                    "No sufficiently relevant approved "
                    "knowledge was found for this incident."
                ),

                "sources": []

            }


        # ====================================================
        # STEP 5: RELEVANCE GATE
        # ====================================================

        best_score = reranked_results[0][
            "score"
        ]


        if best_score < self.RELEVANCE_THRESHOLD:

            return {

                "status": "REJECTED",

                "answer": (
                    "No sufficiently relevant approved "
                    "knowledge was found for this incident."
                ),

                "sources": []

            }


        # ====================================================
        # STEP 6: PREPARE RETRIEVED KNOWLEDGE
        # ====================================================

        retrieved_documents = [

            result["document"]

            for result in reranked_results

        ]


        # ====================================================
        # STEP 7: LLM GENERATION
        # ====================================================

        answer = self.generator.generate(

            query=user_query,

            documents=retrieved_documents

        )


        # ====================================================
        # STEP 8: PREPARE SOURCES
        # ====================================================

        sources = []


        for result in reranked_results:

            for candidate in candidates:

                if candidate["text"] == result["document"]:

                    sources.append({

                        "document": candidate[
                            "document"
                        ],

                        "chunk_number": candidate[
                            "chunk_number"
                        ],

                        "score": result[
                            "score"
                        ]

                    })

                    break


        # ====================================================
        # FINAL RESPONSE
        # ====================================================

        return {

            "status": "ACCEPTED",

            "answer": answer,

            "sources": sources

        }