
from config import get_gemini_client, GEMINI_MODEL
from processing.claim_analyzer import analyze_claim
from processing.decision_engine import make_claim_decision
from tools.search_tool import search_multiple_queries
from tools.retrieval_tool import retrieve_evidence
from tools.evidence_tool import evaluate_evidence
from memory.memory import save_claim, save_evidence


def main():

    # Research claim to verify
    claim = (
        "Artificial intelligence improves student "
        "academic performance."
    )

    print("\nVERIAGENT - EVIDENCE EVALUATION")
    print("=" * 60)

    # Initialize Gemini
    print("\nInitializing Gemini client...")
    client = get_gemini_client()

    # STEP 1: Analyze the research claim
    print("\nStep 1: Analyzing claim...")

    analysis = analyze_claim(
        client,
        GEMINI_MODEL,
        claim
    )

    print("Claim analysis completed!")
    print("Topic:", analysis["topic"])
    print("Claim Type:", analysis["claim_type"])

    # STEP 2: Search academic publications
    print("\nStep 2: Searching academic publications...")

    publications = search_multiple_queries(
        analysis["search_queries"],
        per_page=5
    )

    print("\nPublications retrieved:", len(publications))

    if not publications:
        print("No academic publications found.")
        return

    # STEP 3: Retrieve abstracts
    print("\nStep 3: Retrieving abstracts...")

    evidence = retrieve_evidence(publications)

    # Save the original number before selecting records
    total_abstracts = len(evidence)

    print("Abstracts retrieved:", total_abstracts)

    # Temporarily evaluate only three publications
    evidence = evidence[:3]

    print(
        "Publications selected for evaluation:",
        len(evidence)
    )

    if not evidence:
        print("No evidence records available.")
        return

    # STEP 4: Evaluate research evidence
    print("\nStep 4: Evaluating research evidence...")

    evaluated_evidence = evaluate_evidence(
        client,
        GEMINI_MODEL,
        claim,
        evidence
    )

    # STEP 5: Determine the overall claim verdict
    print("\nStep 5: Making the overall claim decision...")

    decision = make_claim_decision(evaluated_evidence)
    # STEP 6: Save verification results to memory
    print("\nStep 6: Saving verification results to memory...")

    claim_id = save_claim(claim, decision)

    save_evidence(claim_id, evaluated_evidence)

    print("Verification results saved successfully!")
    print("Saved Claim ID:", claim_id)

    print("\nVERIAGENT FINAL DECISION")
    print("=" * 60)

    print("Research Claim:", claim)
    print("Verdict:", decision["verdict"])
    print("Confidence:", decision["confidence"])

    print("\nExplanation:")
    print(decision["explanation"])              

    print("\nEvidence Proportions:")

    for category, proportion in decision["statistics"].get(
        "evidence_proportions", {}
    ).items():
        print(f"{category.capitalize()}: {proportion:.1%}")

    print("\nLimitations:")

    for limitation in decision["limitations"]:
        print("-", limitation)

    # STEP 5: Display individual evaluation results
    print("\nEVIDENCE EVALUATION RESULTS")
    print("=" * 60)

    counts = {
        "supporting": 0,
        "contradicting": 0,
        "neutral": 0,
        "insufficient": 0
    }

    strength_counts = {
        "high": 0,
        "medium": 0,
        "low": 0,
        "none": 0
    }

    for number, record in enumerate(
        evaluated_evidence,
        start=1
    ):

        assessment = record.get(
            "evidence_assessment",
            {}
        )

        classification = assessment.get(
            "classification",
            "insufficient"
        )

        relevance = assessment.get(
            "relevance",
            "low"
        )

        study_type = assessment.get(
            "study_type",
            "unknown"
        )

        findings_status = assessment.get(
            "findings_status",
            "no_clear_findings"
        )

        evidence_strength = assessment.get(
            "evidence_strength",
            "none"
        )

        explanation = assessment.get(
            "explanation",
            "No explanation available."
        )

        # Count classifications
        if classification in counts:
            counts[classification] += 1

        # Count evidence strength
        if evidence_strength in strength_counts:
            strength_counts[evidence_strength] += 1

        print(f"\nPublication {number}")
        print("-" * 50)

        print("Title:", record.get("title"))
        print("Year:", record.get("year"))
        print("DOI:", record.get("doi"))

        print("\nEVIDENCE ASSESSMENT")
        print("Classification:", classification)
        print("Relevance:", relevance)
        print("Study Type:", study_type)
        print("Findings Status:", findings_status)
        print("Evidence Strength:", evidence_strength)

        print("\nExplanation:")
        print(explanation)

    # STEP 6: Display classification summary
    print("\nEVALUATION SUMMARY")
    print("=" * 60)

    print("\nEvidence Classification:")

    for category, count in counts.items():
        print(f"{category.capitalize()}: {count}")

    print("\nEvidence Strength:")

    for strength, count in strength_counts.items():
        print(f"{strength.capitalize()}: {count}")

    # STEP 7: Display final statistics
    total_evaluated = len(evaluated_evidence)

    print("\nFINAL STATISTICS")
    print("=" * 60)

    print("Research claim:", claim)
    print("Total publications retrieved:", len(publications))
    print("Total abstracts retrieved:", total_abstracts)
    print(
        "Total publications selected for evaluation:",
        len(evidence)
    )
    print("Total publications evaluated:", total_evaluated)

    print("\nEvidence evaluation test completed!")


if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        print("\nVERIAGENT TEST FAILED")
        print("Error Type:", type(error).__name__)
        print("Error Message:", error)
