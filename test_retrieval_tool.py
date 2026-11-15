from config import get_gemini_client, GEMINI_MODEL

from processing.claim_analyzer import analyze_claim
from tools.search_tool import search_multiple_queries
from tools.retrieval_tool import retrieve_evidence


def main():

    claim = (
        "Artificial intelligence improves student "
        "academic performance."
    )

    print("\nVERIAGENT - EVIDENCE RETRIEVAL")
    print("=" * 55)

    # Step 1: Analyze the claim
    print("\nStep 1: Analyzing claim...")

    client = get_gemini_client()

    analysis = analyze_claim(
        client,
        GEMINI_MODEL,
        claim
    )

    # Step 2: Search publications
    print("\nStep 2: Searching academic publications...")

    publications = search_multiple_queries(
        analysis["search_queries"],
        per_page=5
    )

    print("Publications retrieved:", len(publications))

    # Step 3: Retrieve abstracts
    print("\nStep 3: Retrieving research abstracts...")

    evidence = retrieve_evidence(publications)

    # Step 4: Display evidence
    print("\nRETRIEVED RESEARCH EVIDENCE")
    print("=" * 55)

    available = 0

    for number, record in enumerate(evidence, start=1):

        print(f"\nPublication {number}")
        print("-" * 45)

        print("Title:", record["title"])
        print("Year:", record["year"])
        print("Journal:", record["journal"])

        if record["evidence_available"]:

            available += 1

            print("\nAbstract:")
            print(record["abstract"])

        else:
            print("\nAbstract: Not available")

    print("\nSUMMARY")
    print("=" * 55)

    print("Total publications:", len(evidence))
    print("Abstracts retrieved:", available)
    print("Abstracts unavailable:", len(evidence) - available)


if __name__ == "__main__":
    main()