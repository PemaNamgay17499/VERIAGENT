
from processing.evidence_combiner import combine_evaluated_evidence


# Evidence from the first research round
original_evidence = [
    {
        "publication_id": "W123",
        "title": "AI and Student Performance",
        "classification": "supporting"
    },
    {
        "publication_id": "W456",
        "title": "Artificial Intelligence in Education",
        "classification": "neutral"
    }
]


# Evidence from the adaptive research round
additional_evidence = [
    {
        "publication_id": "W456",
        "title": "Artificial Intelligence in Education",
        "classification": "neutral"
    },
    {
        "publication_id": "W789",
        "title": "Impact of AI on Academic Achievement",
        "classification": "contradicting"
    }
]


# Combine both research rounds
combined_evidence = combine_evaluated_evidence(
    original_evidence,
    additional_evidence
)


# Display results
print("\nVERIAGENT - EVIDENCE COMBINATION TEST")
print("=" * 50)

print(f"Original evidence: {len(original_evidence)}")
print(f"Additional evidence: {len(additional_evidence)}")
print(f"Combined unique evidence: {len(combined_evidence)}")

print("\nCombined publications:")

for evidence in combined_evidence:
    print(
        f"- {evidence['title']} "
        f"({evidence['publication_id']})"
    )

print("\nEvidence combination test completed!")
