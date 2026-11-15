
from config import get_gemini_client, GEMINI_MODEL

from processing.adaptive_planner import generate_adaptive_queries


def main():

    print("VERIAGENT - ADAPTIVE PLANNING TEST")
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
        "summary": (
            "The available research evidence is limited."
        ),

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

    print("\nStep 1: Initializing Gemini...")

    client = get_gemini_client()

    print("Gemini initialized successfully!")

    print("\nStep 2: Generating adaptive research queries...")

    plan = generate_adaptive_queries(
        client,
        GEMINI_MODEL,
        claim,
        original_queries,
        reflection
    )

    print("\nStep 3: Adaptive planning results")
    print("=" * 55)

    print("\nStatus:", plan["status"])

    print("\nReason:")
    print(plan["reason"])

    print("\nNew search queries:")

    for index, query in enumerate(
        plan["new_search_queries"],
        start=1
    ):
        print(f"{index}. {query}")

    print("\nAdaptive planning test completed!")


if __name__ == "__main__":
    main()
