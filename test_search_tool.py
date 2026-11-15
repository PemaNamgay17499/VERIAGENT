from config import get_gemini_client, GEMINI_MODEL
from processing.claim_analyzer import analyze_claim
from tools.search_tool import search_multiple_queries


def main():

    claim = (
        "Artificial intelligence improves student "
        "academic performance."
    )

    print("\nVERIAGENT - RESEARCH SEARCH TOOL")
    print("=" * 50)

    # Step 1: Analyze the claim
    print("\nStep 1: Analyzing research claim...")

    client = get_gemini_client()

    analysis = analyze_claim(
        client,
        GEMINI_MODEL,
        claim
    )

    print("Claim analysis completed.")

    # Step 2: Extract search queries
    queries = analysis["search_queries"]

    print("\nStep 2: Generated research queries")

    for query in queries:
        print("-", query)

    # Step 3: Search academic publications
    print("\nStep 3: Searching OpenAlex...")

    publications = search_multiple_queries(
        queries,
        per_page=5
    )

    # Step 4: Display results
    print("\nRESEARCH PUBLICATIONS FOUND")
    print("=" * 50)

    if not publications:
        print("No publications found.")
        return

    for number, publication in enumerate(
        publications, start=1
    ):

        print(f"\nPublication {number}")
        print("-" * 40)

        print("Title:", publication["title"])
        print("Year:", publication["publication_year"])
        print("Authors:", ", ".join(publication["authors"]))
        print("Journal:", publication["journal"])
        print("Citations:", publication["cited_by_count"])
        print("DOI:", publication["doi"])
        print("OpenAlex ID:", publication["id"])

    print("\nTotal unique publications:", len(publications))


if __name__ == "__main__":
    main()