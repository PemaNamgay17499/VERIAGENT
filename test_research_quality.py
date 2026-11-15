
from config import get_gemini_client, GEMINI_MODEL

from processing.research_quality import (
    evaluate_research_quality
)


def main():

    print("=" * 60)
    print("VERIAGENT - RESEARCH QUALITY EVALUATOR TEST")
    print("=" * 60)

    client = get_gemini_client()
    model = GEMINI_MODEL

    claim = "Artificial intelligence improves student academic performance."

    test_publications = [

        {
            "title": "Impact of AI-based tutoring on student mathematics achievement",
            "abstract": """
            This randomized controlled trial investigated the effects
            of an AI-based tutoring system on mathematics achievement.
            A total of 200 university students participated. Students
            were randomly assigned to an AI tutoring group and a
            traditional learning group. The study compared examination
            scores before and after the intervention.
            """
        },

        {
            "title": "Artificial intelligence in cardiovascular healthcare",
            "abstract": """
            This systematic review examined the application of artificial
            intelligence in cardiovascular diagnosis, early detection,
            and clinical decision-making. Eleven randomized controlled
            trials were included in the review.
            """
        },

        {
            "title": "Student satisfaction with AI-powered learning platforms",
            "abstract": """
            This study investigated student satisfaction, motivation,
            and attitudes toward AI-powered learning platforms.
            A survey was conducted among university students.
            The research focused on technology acceptance and
            student perceptions.
            """
        }
    ]

    print("\nResearch claim:")
    print(claim)

    print("\nTesting publications:", len(test_publications))

    results = evaluate_research_quality(
        client,
        model,
        claim,
        test_publications
    )

    print("\n" + "=" * 60)
    print("RESEARCH QUALITY ASSESSMENT RESULTS")
    print("=" * 60)

    for index, record in enumerate(results, start=1):

        assessment = record["quality_assessment"]

        print(f"\nPublication {index}:")
        print("Title:", record["title"])

        print(
            "Relevance score:",
            assessment["relevance_score"]
        )

        print(
            "Outcome alignment:",
            assessment["outcome_alignment"]
        )

        print(
            "Study type:",
            assessment["study_type"]
        )

        print(
            "Quality level:",
            assessment["quality_level"]
        )

        print(
            "Recommendation:",
            assessment["recommendation"]
        )

        print(
            "Eligible for decision:",
            assessment["eligible_for_decision"]
        )

        print("Reasoning:", assessment["reasoning"])

    eligible_count = sum(
        1 for record in results
        if record["quality_assessment"]["eligible_for_decision"]
    )

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    print("Publications assessed:", len(results))
    print("Eligible publications:", eligible_count)
    print("Excluded or cautious publications:", len(results) - eligible_count)

    print("\nResearch quality evaluator test completed!")


if __name__ == "__main__":
    main()
