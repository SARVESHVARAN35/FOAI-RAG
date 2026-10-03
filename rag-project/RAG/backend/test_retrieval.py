from pathlib import Path
import json

from app.rag.embeddings import generate_embedding
from app.rag.vector_store import VectorStore
from app.rag.reranker import Reranker


# ============================================================
# CONFIGURATION
# ============================================================

vector_store_path = Path(
    "vector_store/knowledge.index"
)

metadata_path = Path(
    "vector_store/metadata.json"
)

# Prototype relevance threshold
RELEVANCE_THRESHOLD = 1.0


# ============================================================
# LOAD FAISS INDEX
# ============================================================

print("=" * 70)
print("Loading FAISS cosine similarity index")
print("=" * 70)

store = VectorStore()

store.load(
    str(vector_store_path)
)

print(
    "Vectors loaded:",
    store.index.ntotal
)


# ============================================================
# LOAD METADATA
# ============================================================

with open(
    metadata_path,
    "r",
    encoding="utf-8"
) as file:

    metadata = json.load(file)


print(
    "Metadata entries:",
    len(metadata)
)


# ============================================================
# LOAD CROSS-ENCODER
# ============================================================

print("\n" + "=" * 70)
print("Loading Cross-Encoder Reranker")
print("=" * 70)

reranker = Reranker()


# ============================================================
# TEST QUERY FUNCTION
# ============================================================

def test_query(
    query,
    retrieval_k=5,
    final_k=3
):

    print("\n" + "=" * 70)
    print("QUERY")
    print("=" * 70)

    print(query)


    # --------------------------------------------------------
    # STEP 1: CREATE QUERY EMBEDDING
    # --------------------------------------------------------

    query_embedding = generate_embedding(
        query
    )


    # --------------------------------------------------------
    # STEP 2: FAISS RETRIEVAL
    # --------------------------------------------------------

    similarities, indices = store.search(
        query_embedding,
        top_k=retrieval_k
    )


    print("\n" + "-" * 70)
    print("FAISS CANDIDATES")
    print("-" * 70)


    candidates = []


    for rank, (similarity, index) in enumerate(
        zip(similarities, indices),
        start=1
    ):

        if index == -1:
            continue


        document_info = metadata[index]


        candidate = {

            "faiss_rank": rank,

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
        }


        candidates.append(
            candidate
        )


        print(
            f"\nFAISS Rank: {rank}"
        )

        print(
            "Cosine Similarity:",
            round(
                float(similarity),
                4
            )
        )

        print(
            "Document:",
            document_info["document"]
        )

        print(
            "Chunk:",
            document_info["chunk_number"]
        )


    # --------------------------------------------------------
    # STEP 3: PREPARE DOCUMENTS FOR RERANKING
    # --------------------------------------------------------

    candidate_texts = [

        candidate["text"]

        for candidate in candidates

    ]


    # --------------------------------------------------------
    # STEP 4: CROSS-ENCODER RERANKING
    # --------------------------------------------------------

    reranked_results = reranker.rerank(

        query=query,

        documents=candidate_texts,

        top_k=final_k

    )


    # --------------------------------------------------------
    # STEP 5: CHECK WHETHER ANY RESULT EXISTS
    # --------------------------------------------------------

    if not reranked_results:

        print("\n" + "-" * 70)
        print("RELEVANCE GATE")
        print("-" * 70)

        print(
            "\n❌ REJECTED"
        )

        print(
            "No sufficiently relevant approved knowledge "
            "was found for this incident."
        )

        return


    # --------------------------------------------------------
    # STEP 6: RELEVANCE GATE
    # --------------------------------------------------------

    best_score = reranked_results[0][
        "score"
    ]


    print("\n" + "-" * 70)
    print("RELEVANCE GATE")
    print("-" * 70)


    print(
        "Best Cross-Encoder Score:",
        round(
            best_score,
            4
        )
    )


    print(
        "Relevance Threshold:",
        RELEVANCE_THRESHOLD
    )


    # --------------------------------------------------------
    # REJECT IRRELEVANT QUERY
    # --------------------------------------------------------

    if best_score < RELEVANCE_THRESHOLD:

        print(
            "\n❌ REJECTED"
        )

        print(
            "No sufficiently relevant approved knowledge "
            "was found for this incident."
        )

        return


    # --------------------------------------------------------
    # ACCEPT RELEVANT QUERY
    # --------------------------------------------------------

    print(
        "\n✅ ACCEPTED"
    )

    print(
        "Relevant knowledge found."
    )


    # --------------------------------------------------------
    # STEP 7: DISPLAY RERANKED RESULTS
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("CROSS-ENCODER RERANKED RESULTS")
    print("-" * 70)


    for rank, result in enumerate(
        reranked_results,
        start=1
    ):

        matching_candidate = None


        for candidate in candidates:

            if candidate["text"] == result["document"]:

                matching_candidate = candidate

                break


        if matching_candidate is None:
            continue


        print(
            f"\nReranked Rank: {rank}"
        )


        print(
            "Cross-Encoder Score:",
            round(
                result["score"],
                4
            )
        )


        print(
            "Original FAISS Rank:",
            matching_candidate[
                "faiss_rank"
            ]
        )


        print(
            "Cosine Similarity:",
            round(
                matching_candidate[
                    "faiss_similarity"
                ],
                4
            )
        )


        print(
            "Document:",
            matching_candidate[
                "document"
            ]
        )


        print(
            "Chunk:",
            matching_candidate[
                "chunk_number"
            ]
        )


        print(
            "Text:",
            matching_candidate[
                "text"
            ]
        )


# ============================================================
# RELEVANT QUERIES
# ============================================================

queries = [

    "My Payment API is giving 504 Gateway Timeout after deployment. What should I check?",

    "The application cannot connect to the database and database requests are timing out.",

    "My API is returning HTTP 500 Internal Server Error. How can I troubleshoot it?",

    "I cannot authenticate or log in to the company VPN.",

    "The application is unable to connect to Redis and the Redis connection keeps failing.",

    "After a recent deployment, the payment service waits too long and eventually times out.",

]


# ============================================================
# RUN RELEVANT QUERY TESTS
# ============================================================

print("\n\n")

print(
    "#" * 70
)

print(
    "# RELEVANT KNOWLEDGE TESTS"
)

print(
    "#" * 70
)


for query in queries:

    test_query(

        query=query,

        retrieval_k=5,

        final_k=3

    )


# ============================================================
# IRRELEVANT QUERIES
# ============================================================

irrelevant_queries = [

    "What is the company's employee leave policy?",

    "How do I increase the brightness of my laptop screen?",

]


# ============================================================
# RUN IRRELEVANT QUERY TESTS
# ============================================================

print("\n\n")

print(
    "#" * 70
)

print(
    "# IRRELEVANT QUERY TESTS"
)

print(
    "#" * 70
)


for query in irrelevant_queries:

    test_query(

        query=query,

        retrieval_k=5,

        final_k=3

    )


# ============================================================
# COMPLETION
# ============================================================

print("\n\n")

print(
    "=" * 70
)

print(
    "RETRIEVAL + RERANKING + RELEVANCE GATE TESTING COMPLETED"
)

print(
    "=" * 70
)

print(
    "First stage:",
    "FAISS Cosine Similarity"
)

print(
    "Candidate count:",
    5
)

print(
    "Second stage:",
    "Cross-Encoder Reranking"
)

print(
    "Final results:",
    3
)

print(
    "Relevance threshold:",
    RELEVANCE_THRESHOLD
)

print(
    "Fallback:",
    "No sufficiently relevant approved knowledge "
    "was found for this incident."
)

print(
    "=" * 70
)