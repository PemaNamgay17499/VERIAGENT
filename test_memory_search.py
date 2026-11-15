
from memory.memory import search_similar_claims

print("VERIAGENT MEMORY SEARCH TEST")
print("=" * 50)

claim = "Artificial intelligence improves student academic performance."

print("\nSearching previous verification cases...")

results = search_similar_claims(claim)

if results:

    print("\nPrevious cases found:", len(results))

    for record in results:

        print("\nClaim ID:", record["id"])
        print("Claim:", record["claim"])
        print("Verdict:", record["verdict"])
        print("Confidence:", record["confidence"])

else:

    print("\nNo matching previous claims found.")

print("\nMemory search test completed!")
