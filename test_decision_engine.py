
from processing.decision_engine import make_claim_decision


def create_publication(
    classification,
    relevance="high",
    strength="high",
    study_type="empirical_study",
    findings_status="actual_positive_findings"
):
    """
    Create sample publication records
    for testing the decision engine.
    """

    return {
        "title": "Sample Research Publication",
        "evidence_assessment": {
            "classification": classification,
            "relevance": relevance,
            "evidence_strength": strength,
            "study_type": study_type,
            "findings_status": findings_status
        }
    }


def run_test(test_name, publications, expected_verdict):

    print("\n" + "=" * 60)
    print("TEST:", test_name)
    print("=" * 60)

    decision = make_claim_decision(publications)

    print("Expected Verdict:", expected_verdict)
    print("Actual Verdict:", decision["verdict"])
    print("Confidence:", decision["confidence"])

    print("\nExplanation:")
    print(decision["explanation"])

    print("\nPublication Counts:")
    for category, count in decision["statistics"][
        "publication_counts"
    ].items():
        print(f"{category.capitalize()}: {count}")

    print("\nWeighted Evidence Scores:")
    for category, score in decision["statistics"][
        "weighted_scores"
    ].items():
        print(f"{category.capitalize()}: {score:.2f}")

    print("\nLimitations:")
    for limitation in decision["limitations"]:
        print("-", limitation)

    if decision["verdict"] == expected_verdict:
        print("\nTEST RESULT: PASSED")
    else:
        print("\nTEST RESULT: FAILED")

    return decision["verdict"] == expected_verdict


def main():

    print("\nVERIAGENT - DECISION ENGINE TEST")
    print("=" * 60)

    # TEST 1: Supported
    supported_publications = [
        create_publication("supporting"),
        create_publication("supporting"),
        create_publication("supporting")
    ]

    # TEST 2: Contradicted
    contradicted_publications = [
        create_publication(
            "contradicting",
            findings_status="actual_negative_findings"
        ),
        create_publication(
            "contradicting",
            findings_status="actual_negative_findings"
        ),
        create_publication(
            "contradicting",
            findings_status="actual_negative_findings"
        )
    ]

    # TEST 3: Partially Supported
    partially_supported_publications = [
        create_publication("supporting"),
        create_publication("supporting"),
        create_publication(
            "neutral",
            findings_status="mixed_findings"
        )
    ]

    # TEST 4: Inconclusive
    inconclusive_publications = [
        create_publication("supporting"),
        create_publication(
            "contradicting",
            findings_status="actual_negative_findings"
        ),
        create_publication(
            "neutral",
            findings_status="mixed_findings"
        )
    ]

    # Run all four tests
    results = []

    results.append(
        run_test(
            "Supporting Evidence",
            supported_publications,
            "Supported"
        )
    )

    results.append(
        run_test(
            "Contradicting Evidence",
            contradicted_publications,
            "Contradicted"
        )
    )

    results.append(
        run_test(
            "Partially Supporting Evidence",
            partially_supported_publications,
            "Partially Supported"
        )
    )

    results.append(
        run_test(
            "Mixed Evidence",
            inconclusive_publications,
            "Inconclusive"
        )
    )

    # Final test summary
    print("\n" + "=" * 60)
    print("FINAL TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    failed = len(results) - passed

    print("Total Tests:", len(results))
    print("Passed:", passed)
    print("Failed:", failed)

    if failed == 0:
        print("\nALL DECISION ENGINE TESTS PASSED!")

    else:
        print("\nSOME TESTS FAILED. CHECK THE RESULTS.")


if __name__ == "__main__":
    main()
