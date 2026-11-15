
import json
import re


def reflect_on_feedback(client, model, feedback_records):
    """
    Analyze previous user feedback and generate recommendations
    for improving future verification processes.

    User feedback is treated as guidance, not scientific evidence.
    """

    if not feedback_records:
        return {
            "status": "no_feedback",
            "summary": "No previous user feedback is available.",
            "recurring_concerns": [],
            "recommendations": []
        }

    feedback_text = "\n".join(
        f"- {record['user_feedback']}"
        for record in feedback_records
    )

    prompt = f"""
You are the reflection component of VeriAgent,
an AI research claim verification agent.

Your task is to analyze feedback from users about
previous research verification results.

USER FEEDBACK:
{feedback_text}

Instructions:
1. Identify the main concerns expressed by users.
2. Identify recurring concerns if multiple feedback
   records are available.
3. Recommend practical improvements to the future
   research verification process.
4. Do not treat user agreement or disagreement as
   scientific evidence.
5. Do not change previous verification verdicts.
6. Do not invent feedback or research findings.

Return ONLY valid JSON in this format:

{{
    "summary": "A short summary of the feedback.",
    "recurring_concerns": [
        "Concern 1"
    ],
    "recommendations": [
        "Recommendation 1"
    ]
}}
"""

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        response_text = response.text.strip()

        # Remove Markdown code fences if Gemini includes them.
        response_text = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            response_text,
            flags=re.IGNORECASE
        )

        result = json.loads(response_text)

        if not isinstance(result, dict):
            raise ValueError("Gemini returned an invalid JSON structure.")

        return {
            "status": "completed",
            "summary": result.get("summary", ""),
            "recurring_concerns": result.get(
                "recurring_concerns", []
            ),
            "recommendations": result.get(
                "recommendations", []
            )
        }

    except Exception as error:
        print("Reflection analysis failed:", error)

        return {
            "status": "failed",
            "summary": "Could not analyze previous feedback.",
            "recurring_concerns": [],
            "recommendations": []
        }
