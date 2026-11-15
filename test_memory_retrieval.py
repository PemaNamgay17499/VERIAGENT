
from memory.memory import (
    get_claim_details,
    get_claim_history
)

print("VERIAGENT PERSISTENT MEMORY TEST")
print("=" * 50)

# Retrieve the latest saved verification
claim_id = 2

details = get_claim_details(claim_id)

if details is None:
    print("Claim not found!")
else:
    claim = details["claim"]
    evidence = details["evidence"]

    print("\nSAVED RESEARCH CLAIM")
    print("-" * 50)

    print("Claim ID:", claim["id"])
    print("Claim:", claim["claim"])
    print("Verdict:", claim["verdict"])
    print("Confidence:", claim["confidence"])
    print("Explanation:", claim["explanation"])

    print("\nSAVED RESEARCH EVIDENCE")
    print("-" * 50)

    print("Total evidence records:", len(evidence))

    for index, record in enumerate(evidence, start=1):
        print(f"\nPublication {index}")
        print("Title:", record["title"])
        print("Classification:", record["classification"])
        print("Evidence strength:", record["evidence_strength"])

# Retrieve verification history
print("\nVERIFICATION HISTORY")
print("-" * 50)

history = get_claim_history()

for record in history:
    print(
        f'ID: {record["id"]} | '
        f'Verdict: {record["verdict"]} | '
        f'Claim: {record["claim"]}'
    )

print("\nMemory retrieval test completed!")
