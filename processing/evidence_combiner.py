
def combine_evaluated_evidence(original_evidence, additional_evidence):
    """
    Combine evidence from the original and adaptive research rounds.

    Duplicate publications are identified using their OpenAlex publication ID.
    Original evidence is preserved, and only new publications are added.
    """

    if not isinstance(original_evidence, list):
        raise ValueError("Original evidence must be a list.")

    if not isinstance(additional_evidence, list):
        raise ValueError("Additional evidence must be a list.")

    combined_evidence = []
    seen_publication_ids = set()

    # First, preserve all original evidence.
    for evidence in original_evidence:
        publication_id = evidence.get("publication_id")

        if publication_id:
            if publication_id in seen_publication_ids:
                continue

            seen_publication_ids.add(publication_id)

        combined_evidence.append(evidence)

    # Next, add only new evidence.
    for evidence in additional_evidence:
        publication_id = evidence.get("publication_id")

        if publication_id:
            if publication_id in seen_publication_ids:
                continue

            seen_publication_ids.add(publication_id)

        combined_evidence.append(evidence)

    return combined_evidence
