import json
import re


def analyze_claim(client, model, claim):
    """
    Analyze a research claim and prepare it for verification.
    """

    if not claim or not claim.strip():
        raise ValueError("Please provide a research claim.")

    prompt = f"""
    You are the claim analysis component of VeriAgent,
    an AI agent designed to verify research claims.

    Analyze the following claim and return a structured analysis.

    CLAIM:
    {claim}

    Identify:
    1. The main topic.
    2. Important entities or concepts.
    3. The type of claim (scientific, educational, economic,
       social, technological, health, or other).
    4. The main research questions needed to verify it.
    5. Three useful search queries for finding academic evidence.
    6. Any limitations, ambiguity, or missing context.

    Return ONLY valid JSON using this structure:

    {{
        "original_claim": "The submitted claim",
        "topic": "Main topic",
        "key_entities": ["entity 1", "entity 2"],
        "claim_type": "Type of claim",
        "verification_questions": [
            "Question 1",
            "Question 2"
        ],
        "search_queries": [
            "Search query 1",
            "Search query 2",
            "Search query 3"
        ],
        "limitations": "Ambiguities or missing context"
    }}

    Do not decide whether the claim is true or false.
    Do not invent supporting evidence or citations.
    """

    response = client.interactions.create(
        model=model,
        input=prompt
    )

    result = response.output_text.strip()

    # Remove Markdown code fences if the model adds them.
    result = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        result,
        flags=re.IGNORECASE
    )

    try:
        analysis = json.loads(result)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Could not interpret the AI analysis as JSON: {error}"
        )

    # Basic validation of the expected output.
    required_fields = [
        "original_claim",
        "topic",
        "key_entities",
        "claim_type",
        "verification_questions",
        "search_queries",
        "limitations"
    ]

    for field in required_fields:
        if field not in analysis:
            raise ValueError(
                f"AI analysis is missing the field: {field}"
            )

    return analysis