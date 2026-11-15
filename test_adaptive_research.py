
from processing.adaptive_research import conduct_adaptive_research
from processing.adaptive_planner import generate_adaptive_queries

from config import get_gemini_client, GEMINI_MODEL

from tools.search_tool import search_multiple_queries


def main():

    print("VERIAGENT - ADAPTIVE RESEARCH TEST")
    print("=" * 55)

    claim = (
        "Artificial intelligence improves "
        "student academic performance."
    )

    original_queries = [
        "artificial intelligence impact on student academic performance",
        "AI tools in education learning outcomes empirical studies",
        "systematic review AI in education academic achievement"
    ]

    reflection = {
        "summary": "Available research evidence is limited.",

        "recurring_concerns": [
            "Insufficient evidence",
            "Limited empirical research"
        ],

        "recommendations": [
            "Retrieve more empirical studies.",
            "Expand academic literature searches.",
            "Cross-reference additional research."
        ]
    }

    # Step 1: Initialize Gemini
    print("\nStep 1: Initializing Gemini...")

    client = get_gemini_client()

    # Step 2: Retrieve original publications
    print("\nStep 2: Retrieving original publications...")

    original_publications = search_multiple_queries(
        original_queries,
        per_page=5
    )

    print(
        "\nOriginal publications:",
        len(original_publications)
    )

    # Step 3: Generate adaptive search queries
    print("\nStep 3: Generating new search queries...")

    plan = generate_adaptive_queries(
        client,
        GEMINI_MODEL,
        claim,
        original_queries,
        reflection
    )

    if plan["status"] != "completed":
        print("Adaptive planning failed.")
        return

    print("\nNew search queries:")

    for query in plan["new_search_queries"]:
        print("-", query)

    # Step 4: Conduct second research round
    print("\nStep 4: Conducting adaptive research...")

    adaptive_result = conduct_adaptive_research(
        plan["new_search_queries"],
        original_publications
    )

    # Step 5: Display summary
    print("\nADAPTIVE RESEARCH SUMMARY")
    print("=" * 55)

    print(
        "Original publications:",
        len(original_publications)
    )

    print(
        "New unique publications:",
        len(adaptive_result["new_publications"])
    )

    print(
        "New abstracts retrieved:",
        len(adaptive_result["new_evidence"])
    )

    print(
        "\nStatus:",
        adaptive_result["status"]
    )

    print("\nAdaptive research test completed!")


if __name__ == "__main__":
    main()
