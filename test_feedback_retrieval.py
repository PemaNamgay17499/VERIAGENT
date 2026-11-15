from memory.memory import get_feedback

print("VERIAGENT - FEEDBACK RETRIEVAL TEST")
print("=" * 50)

claim_id = 6

print(f"\nRetrieving feedback for Claim ID: {claim_id}")

feedback_records = get_feedback(claim_id)

if feedback_records:

    print("\nFeedback records found:", len(feedback_records))

    for record in feedback_records:
        print("\nFeedback ID:", record["id"])
        print("Claim ID:", record["claim_id"])
        print("User Feedback:", record["user_feedback"])
        print("Created At:", record["created_at"])

else:
    print("\nNo feedback found.")

print("\nFeedback retrieval test completed!")