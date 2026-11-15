import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)


def get_gemini_client():
    """Create a Gemini API client."""

    if not GEMINI_API_KEY:
        raise ValueError(
            "Gemini API key not found. Check your .env file."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY,
        http_options={
            "timeout": 120000
        }
    )