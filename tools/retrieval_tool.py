
def reconstruct_abstract(inverted_index):
    """
    Convert OpenAlex's inverted abstract index
    into normal readable text.
    """

    if not inverted_index:
        return None

    words = {}

    for word, positions in inverted_index.items():

        for position in positions:
            words[position] = word

    if not words:
        return None

    abstract = " ".join(
        words[position]
        for position in sorted(words)
    )

    return abstract


def retrieve_evidence(publications):
    """
    Extract abstracts from OpenAlex and Crossref publications.

    Returns structured evidence records.
    """

    evidence_records = []

    for publication in publications:

        # Crossref supplies plain-text abstracts.
        # OpenAlex supplies inverted-index abstracts.
        abstract = publication.get("abstract")

        if not abstract:

            abstract = reconstruct_abstract(
                publication.get("abstract_inverted_index")
            )

        record = {
            "publication_id": publication.get("id"),
            "title": publication.get("title"),
            "year": publication.get("publication_year"),
            "authors": publication.get("authors", []),
            "journal": publication.get("journal"),
            "doi": publication.get("doi"),
            "citation_count": publication.get(
                "cited_by_count", 0
            ),
            "abstract": abstract,
            "pdf_url": publication.get("pdf_url"),
            "evidence_available": bool(abstract),
            "source": publication.get("source", "OpenAlex")
        }

        evidence_records.append(record)

    return evidence_records
