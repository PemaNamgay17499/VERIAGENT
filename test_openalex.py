
from tools.search_tool import search_publications
from tools.retrieval_tool import retrieve_evidence

query = "artificial intelligence education"

print("\nTesting VeriAgent academic search...")
print("=" * 55)

try:

    publications = search_publications(
        query,
        per_page=3
    )

    print("\nPublications retrieved:", len(publications))

    evidence = retrieve_evidence(publications)

    print("Evidence records created:", len(evidence))

    for item in evidence:

        print("\nTitle:", item["title"])
        print("Year:", item["year"])
        print("DOI:", item["doi"])
        print("Abstract available:", item["evidence_available"])
        print("Provider:", item["source"])

    print("\nAcademic search test completed.")

except Exception as error:

    print("\nTest failed:")
    print(error)
