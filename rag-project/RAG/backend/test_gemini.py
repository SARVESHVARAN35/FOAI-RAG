from dotenv import load_dotenv
from google import genai
import os


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=api_key
)


interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input="Explain HTTP 504 Gateway Timeout in one sentence."
)


print("\nGemini Response:")
print(interaction.output_text)