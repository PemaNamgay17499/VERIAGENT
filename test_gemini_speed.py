
import time
from config import get_gemini_client, GEMINI_MODEL

print("Initializing Gemini client...")

try:
    client = get_gemini_client()

    print("Client initialized.")
    print("Testing model:", GEMINI_MODEL)

    start = time.time()

    print("\nSending request to Gemini...")

    response = client.interactions.create(
        model=GEMINI_MODEL,
        input="Reply with only the word SUCCESS."
    )

    elapsed = time.time() - start

    print("\nGemini response:", response.output_text)
    print(f"Response time: {elapsed:.2f} seconds")

except Exception as error:
    print("\nGemini request failed:")
    print(type(error).__name__, error)
