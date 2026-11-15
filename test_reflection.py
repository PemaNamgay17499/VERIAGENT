
from config import get_gemini_client, GEMINI_MODEL

from memory.memory import get_feedback

from processing.reflection import reflect_on_feedback


def main():

    print("VERIAGENT - REFLECTION TEST")
    print("=" * 50)

    # Retrieve previous feedback
    claim_id = 6

    print("\nStep 1: Retrieving previous feedback...")

    feedback_records = get_feedback(claim_id)

    print("Feedback records found:", len(feedback_records))

    if not feedback_records:
        print("No feedback available for reflection.")
        return

    # Initialize Gemini
    print("\nStep 2: Initializing Gemini...")

    client = get_gemini_client()

    # Analyze feedback
    print("\nStep 3: Analyzing user feedback...")

    reflection = reflect_on_feedback(
        client,
        GEMINI_MODEL,
        feedback_records
    )

    # Display results
    print("\nSTEP 4: REFLECTION RESULTS")
    print("=" * 50)

    print("\nStatus:", reflection["status"])

    print("\nSummary:")
    print(reflection["summary"])

    print("\nRecurring Concerns:")

    for concern in reflection["recurring_concerns"]:
        print("-", concern)

    print("\nRecommendations:")

    for recommendation in reflection["recommendations"]:
        print("-", recommendation)

    print("\nReflection test completed!")


if __name__ == "__main__":
    main()
