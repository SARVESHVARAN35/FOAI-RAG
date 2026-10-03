from app.rag.generator import Generator


generator = Generator()


query = (
    "My Payment API is giving 504 Gateway Timeout "
    "after deployment. What should I check?"
)


documents = [

    """
    ## Symptoms

    Users receive HTTP 504 Gateway Timeout responses when
    accessing the Payment API after a new deployment.
    Requests may take a long time before failing.
    """,

    """
    ## Root Cause

    A deployment introduced a backend timeout configuration
    that was lower than the time required for certain
    Payment API operations. The gateway stopped waiting
    before the backend completed processing.
    """,

    """
    ## Troubleshooting Steps

    1. Check the Payment API application logs for slow or
       incomplete requests.
    2. Check the gateway and backend timeout configuration.
    3. Compare the current deployment configuration with the
       previous working configuration.
    4. Check whether backend response times increased after deployment.
    5. Verify that the Payment API service is running correctly.
    """,

    """
    ## Resolution

    Adjust the gateway and backend timeout configuration to
    an appropriate value based on the expected processing time.
    Validate the configuration and redeploy the service.
    """
]


answer = generator.generate(
    query=query,
    documents=documents
)


print("\n" + "=" * 70)
print("GENERATED RAG ANSWER")
print("=" * 70)

print(answer)

print("=" * 70)