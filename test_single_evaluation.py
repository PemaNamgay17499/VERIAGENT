from config import get_gemini_client, GEMINI_MODEL


def main():

    client = get_gemini_client()

    claim = "Artificial intelligence improves student academic performance."

    abstract = """
    This study examined the effects of artificial intelligence
    on student academic achievement. The results showed that
    students using AI-based learning tools achieved higher
    academic performance than students in the comparison group.
    """

    prompt = f"""
Evaluate the following abstract against the claim.

CLAIM:
{claim}

ABSTRACT:
{abstract}

Return ONLY JSON:

{{
    "classification": "supporting",
    "explanation": "short explanation",
    "relevance": "high"
}}

Use only the information provided.
"""

    print("Sending evaluation request to Gemini...")

    response = client.interactions.create(
        model=GEMINI_MODEL,
        input=prompt
    )

    print("\nGemini responded successfully.")
    print(response.output_text)


if __name__ == "__main__":
    main()