import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-3.5-flash-lite"

URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL}:generateContent"
)

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

print("Testing Gemini generation endpoint directly...")
print("Model:", MODEL)

payload = {
    "contents": [
        {
            "parts": [
                {"text": "Reply with only the word SUCCESS."}
            ]
        }
    ],
    "generationConfig": {
        "maxOutputTokens": 30
    }
}

try:
    start = time.time()

    response = requests.post(
        URL,
        params={"key": API_KEY},
        json=payload,
        timeout=(10, 60)
    )

    elapsed = time.time() - start

    print("\nHTTP Status:", response.status_code)
    print("Response time:", round(elapsed, 2), "seconds")

    if response.status_code == 200:
        data = response.json()

        print("\nFull API response:")
        print(response.text[:3000])

        print("\nResponse structure:")
        print(list(data.keys()))

    else:
        print("API Error:", response.text[:1500])

except requests.exceptions.Timeout:
    print("The direct API request timed out.")

except requests.exceptions.RequestException as error:
    print("Connection error:", error)

except (KeyError, IndexError) as error:
    print("Unexpected API response:", error)