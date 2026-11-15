
from memory.memory import (
    save_claim,
    save_evidence,
    get_claim_history,
    get_claim_details,
    save_feedback
)

print("VERIAGENT MEMORY TEST")
print("=" * 50)

# Test 1: Save a research claim
print("\nTest 1: Saving a research claim...")

claim = "Artificial intelligence improves student academic performance."

decision = {
    "verdict": "Inconclusive",
    "confidence": "Low",
    "explanation": "The available research evidence is mixed."
}

claim_id = save_claim(claim, decision)

print("Claim saved successfully!")
print("Claim ID:", claim_id)


# Test 2: Save evaluated research evidence
print("\nTest 2: Saving research evidence...")

evidence = [
    {
        "publication_id": "test_publication_001",
        "title": "AI and Student Academic Performance",
        "year": 2025,
        "doi": "https://doi.org/test",
        "assessment": {
            "classification": "supporting",
            "relevance": "high",
            "study_type": "empirical_study",
            "findings_status": "actual_positive_findings",
            "evidence_strength": "medium",
            "explanation": "The study reports positive findings."
        }
    }
]

save_evidence(claim_id, evidence)

print("Research evidence saved successfully!")


# Test 3: Retrieve claim history
print("\nTest 3: Retrieving claim history...")

history = get_claim_history()

for record in history:
    print("Claim:", record["claim"])
    print("Verdict:", record["verdict"])
    print("Confidence:", record["confidence"])


# Test 4: Retrieve claim details
print("\nTest 4: Retrieving claim details...")

details = get_claim_details(claim_id)

print("Retrieved claim:", details["claim"]["claim"])
print("Retrieved evidence:", len(details["evidence"]))


# Test 5: Save user feedback
print("\nTest 5: Saving user feedback...")

feedback_id = save_feedback(
    claim_id,
    "The result should include more research publications."
)

print("Feedback saved successfully!")
print("Feedback ID:", feedback_id)


print("\n" + "=" * 50)
print("ALL MEMORY TESTS COMPLETED!")
