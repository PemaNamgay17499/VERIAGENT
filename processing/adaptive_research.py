
from tools.search_tool import search_multiple_queries
from tools.retrieval_tool import retrieve_evidence


def conduct_adaptive_research(
    new_search_queries,
    original_publications
):
    """
    Conduct a second research round.

    Searches for additional academic publications,
    removes duplicates, and retrieves new abstracts.
    """

    print("\n" + "=" * 60)
    print("VERIAGENT - ADAPTIVE RESEARCH ROUND")
    print("=" * 60)

    if not new_search_queries:
        print("No new search queries available.")

        return {
            "status": "incomplete",
            "new_publications": [],
            "new_evidence": []
        }

    print("\nStep 1: Searching for additional publications...")

    additional_publications = search_multiple_queries(
        new_search_queries,
        per_page=5
    )

    print(
        "\nPublications retrieved in second round:",
        len(additional_publications)
    )

    # Identify publications already retrieved
    original_ids = {
        publication.get("id")
        for publication in original_publications
        if publication.get("id")
    }

    # Remove duplicate publications
    new_publications = [
        publication
        for publication in additional_publications
        if publication.get("id") not in original_ids
    ]

    print(
        "New unique publications:",
        len(new_publications)
    )

    if not new_publications:

        print("No additional unique publications found.")

        return {
            "status": "completed",
            "new_publications": [],
            "new_evidence": []
        }

    # Retrieve abstracts for new publications
    print("\nStep 2: Retrieving additional research abstracts...")

    new_evidence = retrieve_evidence(
        new_publications
    )

    print(
        "Additional abstracts retrieved:",
        len(new_evidence)
    )

    available_abstracts = sum(
        1
        for record in new_evidence
        if record.get("evidence_available")
    )

    print(
        "Abstracts available for evaluation:",
        available_abstracts
    )

    print("\nAdaptive research round completed!")

    return {
        "status": "completed",
        "new_publications": new_publications,
        "new_evidence": new_evidence
    }
