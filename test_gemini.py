from config import get_gemini_client, GEMINI_MODEL

print("Connecting to Gemini...")

try:
    client = get_gemini_client()

    response = client.interactions.create(
        model=GEMINI_MODEL,
        input=(
            "Introduce yourself as the AI reasoning engine "
            "of VeriAgent in two sentences."
        )
    )

    print("\nGemini connection successful!")
    print("\nGemini response:")
    print(response.output_text)

except Exception as error:
    print("\nGemini connection failed.")
    print("Error:", error)