from dotenv import load_dotenv
from groq import Groq
import os


load_dotenv()


class Generator:

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=api_key
        )

        self.model = "openai/gpt-oss-20b"


    def generate(
        self,
        query: str,
        documents: list[str]
    ):

        if not documents:

            return (
                "No sufficiently relevant approved "
                "knowledge was found for this incident."
            )


        context = "\n\n".join(
            f"[Knowledge Chunk {i + 1}]\n{document}"
            for i, document in enumerate(documents)
        )


        prompt = f"""
You are an Enterprise IT Incident Knowledge Assistant.

Answer the user's incident question using ONLY the
provided approved knowledge.

Do not invent troubleshooting steps, causes, configurations,
or facts that are not supported by the provided knowledge.

If the provided knowledge does not contain enough information
to answer a part of the question, clearly say that the
available knowledge does not provide that information.

Prefer concise, practical troubleshooting guidance.

User Incident:
{query}

Approved Knowledge:
{context}

Answer:
"""


        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an Enterprise IT Incident "
                        "Knowledge Assistant."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )


        return response.choices[0].message.content