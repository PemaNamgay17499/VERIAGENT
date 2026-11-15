import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

url = "https://generativelanguage.googleapis.com/v1beta/models"

print("Checking Gemini API connection...")

try:
    response = requests.get(
        url,
        params={"key": api_key},
        timeout=(10, 20)
    )

    print("HTTP Status:", response.status_code)

    if response.status_code == 200:
        data = response.json()

        print("\nAvailable Gemini models:")

        for model in data.get("models", []):
            name = model.get("name", "")

            if "gemini" in name.lower():
                print(name)

    else:
        print("API response:", response.text[:1000])

except requests.exceptions.Timeout:
    print("Connection timed out.")

except requests.exceptions.RequestException as error:
    print("Connection error:", error)