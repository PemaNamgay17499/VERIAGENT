
import requests
import time
import re
from html.parser import HTMLParser


OPENALEX_URL = "https://api.openalex.org/works"
CROSSREF_URL = "https://api.crossref.org/works"

SELECT_FIELDS = (
    "id,doi,title,publication_year,cited_by_count,"
    "authorships,primary_location,abstract_inverted_index,"
    "best_oa_location"
)


class AbstractTextParser(HTMLParser):
    """Extract readable text from Crossref HTML/XML abstracts."""

    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        cleaned = data.strip()

        if cleaned:
            self.text_parts.append(cleaned)


def clean_abstract(raw_abstract):
    """Convert a Crossref abstract into readable plain text."""

    if not raw_abstract:
        return None

    parser = AbstractTextParser()

    try:
        parser.feed(raw_abstract)
        text = " ".join(parser.text_parts)
    except Exception:
        text = re.sub(r"<[^>]+>", " ", raw_abstract)

    text = re.sub(r"\s+", " ", text).strip()

    return text if text else None


def get_publication_year(item):
    """Extract publication year from Crossref date fields."""

    for field in [
        "published-print",
        "published-online",
        "published",
        "created"
    ]:

        date_info = item.get(field, {})
        date_parts = date_info.get("date-parts", [])

        if date_parts and date_parts[0]:
            return date_parts[0][0]

    return None


def search_openalex(query, per_page=5, max_retries=2):
    """
    Search OpenAlex for academic publications.

    A long Retry-After value is not followed automatically.
    The caller can then use Crossref as a backup.
    """

    params = {
        "search": query,
        "per_page": per_page,
        "select": SELECT_FIELDS
    }

    for attempt in range(max_retries + 1):

        try:
            response = requests.get(
                OPENALEX_URL,
                params=params,
                timeout=25
            )

            if response.status_code == 429:

                retry_after = response.headers.get("Retry-After")

                raise RuntimeError(
                    "OpenAlex rate limit active. "
                    f"Retry-After: {retry_after or 'not provided'}"
                )

            if response.status_code >= 500:

                if attempt < max_retries:

                    wait_time = 5 * (2 ** attempt)

                    print(
                        f"OpenAlex server error. "
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)
                    continue

            response.raise_for_status()

            data = response.json()

            publications = data.get("results", [])

            # Add fields expected by the retrieval module.
            for publication in publications:

                authors = []

                for authorship in publication.get("authorships", []):

                    author = authorship.get("author", {})

                    name = author.get("display_name")

                    if name:
                        authors.append(name)

                publication["authors"] = authors

                location = publication.get("primary_location") or {}
                source = location.get("source") or {}

                publication["journal"] = source.get("display_name")

            return publications

        except requests.exceptions.Timeout:

            if attempt < max_retries:

                wait_time = 5 * (2 ** attempt)

                print(
                    f"OpenAlex timed out. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)
                continue

            raise RuntimeError("OpenAlex request timed out.")

        except requests.exceptions.RequestException as error:

            raise RuntimeError(
                f"OpenAlex connection failed: {error}"
            ) from error

    return []


def search_crossref(query, per_page=5):
    """
    Search Crossref as a backup academic publication provider.

    Results are converted into a structure compatible with
    VeriAgent's existing retrieval module.
    """

    params = {
        "query.bibliographic": query,
        "rows": per_page,
        "select": (
            "DOI,title,author,published-print,published-online,"
            "published,created,container-title,abstract,"
            "is-referenced-by-count,type,URL"
        )
    }

    headers = {
        "User-Agent": "VeriAgent/1.0 (Academic Research Project)"
    }

    try:
        response = requests.get(
            CROSSREF_URL,
            params=params,
            headers=headers,
            timeout=25
        )

        response.raise_for_status()

        data = response.json()

        items = data.get("message", {}).get("items", [])

        publications = []

        for item in items:

            titles = item.get("title", [])

            title = titles[0] if titles else "Untitled publication"

            doi = item.get("DOI")

            if doi:
                publication_id = f"crossref:{doi}"
            else:
                publication_id = item.get("URL")

            if not publication_id:
                continue

            authors = []

            for author in item.get("author", []):

                given = author.get("given", "")
                family = author.get("family", "")

                full_name = f"{given} {family}".strip()

                if full_name:
                    authors.append(full_name)

            journals = item.get("container-title", [])

            journal = journals[0] if journals else None

            abstract = clean_abstract(
                item.get("abstract")
            )

            publication = {
                "id": publication_id,
                "doi": (
                    f"https://doi.org/{doi}"
                    if doi else None
                ),
                "title": title,
                "publication_year": get_publication_year(item),
                "cited_by_count": item.get(
                    "is-referenced-by-count", 0
                ),
                "authors": authors,
                "journal": journal,
                "abstract": abstract,
                "abstract_inverted_index": None,
                "pdf_url": None,
                "source": "Crossref"
            }

            publications.append(publication)

        return publications

    except requests.exceptions.RequestException as error:

        raise RuntimeError(
            f"Crossref search failed: {error}"
        ) from error


def search_publications(query, per_page=5):
    """
    Try OpenAlex first.
    Automatically use Crossref if OpenAlex fails or returns no results.
    """

    try:

        results = search_openalex(
            query,
            per_page=per_page
        )

        if results:
            print("Search provider: OpenAlex")
            return results

        print("OpenAlex returned no results. Trying Crossref...")

    except Exception as error:

        print(f"OpenAlex unavailable: {error}")
        print("Switching to Crossref backup...")

    try:

        results = search_crossref(
            query,
            per_page=per_page
        )

        print("Search provider: Crossref")
        return results

    except Exception as error:

        raise RuntimeError(
            "Both academic search providers failed.\n"
            f"OpenAlex: unavailable\n"
            f"Crossref: {error}"
        ) from error


def search_multiple_queries(queries, per_page=5):
    """
    Search multiple queries using OpenAlex and Crossref fallback.
    Remove duplicate publications.
    """

    all_publications = []
    seen_ids = set()

    for index, query in enumerate(queries):

        if not isinstance(query, str) or not query.strip():
            continue

        print(f"\nSearching: {query}")

        try:

            results = search_publications(
                query,
                per_page=per_page
            )

        except RuntimeError as error:

            print(f"Search failed for this query: {error}")
            continue

        for publication in results:

            publication_id = (
                publication.get("doi")
                or publication.get("id")
            )

            if not publication_id:
                continue

            publication_id = publication_id.lower()

            if publication_id not in seen_ids:

                seen_ids.add(publication_id)
                all_publications.append(publication)

        print(f"Publications retrieved: {len(results)}")

        print(
            f"Unique publications collected: "
            f"{len(all_publications)}"
        )

        if index < len(queries) - 1:
            time.sleep(2)

    if not all_publications:
        raise RuntimeError(
            "No publications could be retrieved from "
            "OpenAlex or Crossref. Both providers may be "
            "temporarily unavailable."
        )

    return all_publications
