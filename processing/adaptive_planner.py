
import json
import re


def generate_adaptive_queries(
    client,
    model,
    claim,
    original_queries,
    reflection
):
    """
    Generate additional academic search queries using
    the initial verification result and user feedback.

    The new queries should target evidence gaps rather
    than simply repeat the original searches.
    """

    if not claim or not claim.strip():
        raise ValueError("Research claim cannot be empty.")

    recommendations = reflection.get(
        "recommendations", []
    )

    concerns = reflection.get(
        "recurring_concerns", []
    )

    prompt = f"""
You are the adaptive research planner of VeriAgent.

Your task is to improve the academic literature search
for a research claim.

RESEARCH CLAIM:
{claim}

ORIGINAL SEARCH QUERIES:
{json.dumps(original_queries, indent=2)}

IDENTIFIED EVIDENCE CONCERNS:
{json.dumps(concerns, indent=2)}

REFLECTION RECOMMENDATIONS:
{json.dumps(recommendations, indent=2)}

Instructions:

1. Generate exactly three new academic search queries.
2. Target gaps in the existing research search.
3. Focus on empirical studies, systematic reviews,
   and relevant research findings.
4. Explore different aspects of the claim.
5. Avoid repeating the original search queries.
6. Do not invent research publications or findings.
7. Keep each query concise and suitable for OpenAlex.

Return ONLY valid JSON in this format:

{{
    "reason": "Why another research round is useful.",
    "new_search_queries": [
        "First new query",
        "Second new query",
        "Third new query"
    ]
}}
"""

    try:

        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        response_text = response.text.strip()

        response_text = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            response_text,
            flags=re.IGNORECASE
        )

        result = json.loads(response_text)

        queries = result.get(
            "new_search_queries", []
        )

        if not isinstance(queries, list):
            raise ValueError("Search queries must be a list.")

        # Remove empty queries and duplicate queries.
        cleaned_queries = []
        seen = {
            query.strip().lower()
            for query in original_queries
            if isinstance(query, str)
        }

        for query in queries:

            if not isinstance(query, str):
                continue

            query = query.strip()

            if not query:
                continue

            if query.lower() in seen:
                continue

            if query.lower() not in seen:
                cleaned_queries.append(query)
                seen.add(query.lower())

        if not cleaned_queries:
            raise ValueError(
                "No new search queries were generated."
            )

        return {
            "status": "completed",
            "reason": result.get("reason", ""),
            "new_search_queries": cleaned_queries[:3]
        }

    except Exception as error:

        print("Adaptive planning failed:", error)

        return {
            "status": "failed",
            "reason": "Could not generate an adaptive research plan.",
            "new_search_queries": []
        }
