from dotenv import load_dotenv
from groq import Groq
import os


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

print(
    "GROQ_API_KEY loaded:",
    bool(api_key)
)


client = Groq(
    api_key=api_key
)


response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "Explain HTTP 504 Gateway Timeout in one sentence."
        }
    ],
    temperature=0.2
)


print("\nGroq Response:")
print(
    response.choices[0].message.content
)