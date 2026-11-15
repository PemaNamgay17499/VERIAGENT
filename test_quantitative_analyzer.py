
from config import get_gemini_client, GEMINI_MODEL

from processing.quantitative_analyzer import (
    analyze_quantitative_evidence
)


def main():

    print("\nVERIAGENT - QUANTITATIVE ANALYSIS TEST")
    print("=" * 55)

    client = get_gemini_client()

    sample_evidence = [
        {
            "publication_id": "TEST001",
            "title": "AI-Supported Learning and Student Performance",
            "year": 2024,
            "doi": None,
            "abstract": (
                "A study involving 250 university students "
                "examined the effects of AI-supported learning. "
                "Students using the AI-supported learning system "
                "achieved a 12% improvement in test scores. "
                "The results showed a statistically significant "
                "difference between groups (p = 0.03), with an "
                "effect size of Cohen's d = 0.45."
            ),
            "evidence_assessment": {
                "classification": "supporting",
                "relevance": "high",
                "study_type": "empirical_study",
                "evidence_strength": "medium"
            }
        }
    ]

    print("\nTesting quantitative evidence extraction...")

    results = analyze_quantitative_evidence(
        client,
        GEMINI_MODEL,
        sample_evidence
    )

    print("\n" + "=" * 55)
    print("QUANTITATIVE ANALYSIS RESULTS")
    print("=" * 55)

    for result in results:

        print("\nPublication:", result["title"])

        assessment = result["quantitative_assessment"]

        print(
            "Quantitative data available:",
            assessment["has_quantitative_data"]
        )

        print(
            "Sample size:",
            assessment["sample_size"]
        )

        print(
            "Percentages:",
            assessment["percentages"]
        )

        print(
            "Effect sizes:",
            assessment["effect_sizes"]
        )

        print(
            "P-values:",
            assessment["p_values"]
        )

        print(
            "Confidence intervals:",
            assessment["confidence_intervals"]
        )

        print(
            "Other statistics:",
            assessment["other_statistics"]
        )

        print(
            "\nSummary:",
            assessment["quantitative_summary"]
        )

    print("\nQuantitative analysis test completed!")


if __name__ == "__main__":
    main()
