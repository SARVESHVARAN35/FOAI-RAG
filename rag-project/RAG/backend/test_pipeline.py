from app.rag.pipeline import RAGPipeline


print("=" * 70)
print("INITIALIZING RAG PIPELINE")
print("=" * 70)

pipeline = RAGPipeline()


# ============================================================
# RELEVANT QUERY
# ============================================================

query = (
    "My Payment API is giving 504 Gateway Timeout "
    "after deployment. What should I check?"
)


print("\n" + "=" * 70)
print("QUERY")
print("=" * 70)

print(query)


result = pipeline.query(
    user_query=query
)


print("\n" + "=" * 70)
print("RAG RESULT")
print("=" * 70)

print("\nStatus:")
print(result["status"])


print("\nAnswer:")
print(result["answer"])


print("\nSources:")

for source in result["sources"]:

    print(
        f"- {source['document']} "
        f"(chunk {source['chunk_number']}, "
        f"score {source['score']:.4f})"
    )


print("\n" + "=" * 70)
print("PIPELINE TEST COMPLETED")
print("=" * 70)


# ============================================================
# IRRELEVANT QUERY
# ============================================================

irrelevant_query = (
    "What is the company's employee leave policy?"
)


print("\n" + "=" * 70)
print("IRRELEVANT QUERY")
print("=" * 70)

print(irrelevant_query)


irrelevant_result = pipeline.query(
    user_query=irrelevant_query
)


print("\n" + "=" * 70)
print("IRRELEVANT QUERY RESULT")
print("=" * 70)

print("\nStatus:")
print(irrelevant_result["status"])


print("\nAnswer:")
print(irrelevant_result["answer"])


print("\nSources:")
print(irrelevant_result["sources"])


print("\n" + "=" * 70)
print("REJECTION TEST COMPLETED")
print("=" * 70)