
from config import get_gemini_client, GEMINI_MODEL

from processing.claim_analyzer import analyze_claim
from processing.decision_engine import make_claim_decision
from processing.reflection import reflect_on_feedback
from processing.adaptive_planner import generate_adaptive_queries
from processing.adaptive_research import conduct_adaptive_research
from processing.evidence_combiner import combine_evaluated_evidence
from processing.quantitative_analyzer import analyze_quantitative_evidence
from processing.research_quality import evaluate_research_quality

from tools.search_tool import search_multiple_queries
from tools.retrieval_tool import retrieve_evidence
from tools.evidence_tool import evaluate_evidence

from memory.memory import (
    save_claim,
    save_evidence,
    get_claim_history,
    save_feedback,
    get_feedback
)


class VeriAgent:
    """
    VeriAgent: AI Agent for Research Claim Verification.

    Workflow:
    1. Claim analysis
    2. Academic research planning
    3. Publication search
    4. Evidence retrieval
    5. Evidence evaluation
    6. Research quality assessment
    7. Initial decision
    8. Memory storage
    9. User feedback
    10. Reflection
    11. Adaptive research
    12. Updated decision
    13. Quantitative analysis
    14. Final report
    """

    def __init__(self):

        print("Initializing VeriAgent...")

        self.client = get_gemini_client()
        self.model = GEMINI_MODEL

        print("VeriAgent initialized successfully!")

    # ==========================================================
    # EVIDENCE FILTERING
    # ==========================================================

    def get_eligible_evidence(self, evidence_records):

        eligible = []

        for record in evidence_records:

            quality = record.get("quality_assessment", {})

            if quality.get("status") != "completed":
                continue

            if not quality.get("eligible_for_decision", False):
                continue

            if quality.get("outcome_alignment") != "direct":
                continue

            if quality.get("recommendation") != "include":
                continue

            if quality.get("relevance_score", 0) < 70:
                continue

            eligible.append(record)

        return eligible

    # ==========================================================
    # FILTERED DECISION
    # ==========================================================

    def make_filtered_decision(self, evidence_records):

        eligible = self.get_eligible_evidence(evidence_records)

        if not eligible:

            return {
                "verdict": "Inconclusive",
                "confidence": "Low",
                "explanation": (
                    "No sufficiently relevant publications with direct "
                    "academic outcome evidence met the inclusion criteria."
                ),
                "limitations": [
                    "Insufficient eligible evidence was available.",
                    "The decision should not be interpreted as evidence "
                    "that the claim is false."
                ]
            }

        return make_claim_decision(eligible)

    # ==========================================================
    # STEP 0 - PREVIOUS HISTORY
    # ==========================================================

    def show_previous_history(self):

        print("\n[STEP 0] Checking previous verification history...")

        history = get_claim_history()

        print(f"Previous verification cases found: {len(history)}")

        for item in history[:5]:

            print(f"\nPrevious Claim ID: {item.get('id')}")
            print(f"Previous Verdict: {item.get('verdict')}")
            print(f"Previous Confidence: {item.get('confidence')}")

        return history

    # ==========================================================
    # INITIAL CLAIM VERIFICATION
    # ==========================================================

    def verify_claim(self, claim):

        if not claim or not claim.strip():

            return {
                "status": "error",
                "message": "Claim cannot be empty."
            }

        result = {
            "status": "started",
            "claim": claim,
            "analysis": None,
            "publications": [],
            "evaluated_evidence": [],
            "eligible_evidence": [],
            "initial_decision": None,
            "adaptive_decision": None,
            "decision": None,
            "claim_id": None,
            "adaptive_claim_id": None,
            "total_publications": 0,
            "total_abstracts": 0,
            "additional_publications": [],
            "additional_evaluations": [],
            "combined_evidence": [],
            "adaptive_queries": [],
            "reflection": None,
            "quantitative_evidence": [],
            "quantitative_status": "not_started",
            "user_feedback": None
        }

        # ------------------------------------------------------
        # STEP 0: HISTORY
        # ------------------------------------------------------

        self.show_previous_history()

        # ------------------------------------------------------
        # STEP 1: CLAIM ANALYSIS
        # ------------------------------------------------------

        print("\n" + "=" * 60)
        print("[STEP 1] Analyzing research claim...")
        print("=" * 60)

        analysis = analyze_claim(
            self.client,
            self.model,
            claim
        )

        result["analysis"] = analysis

        print("\nClaim topic:")
        print(analysis.get("topic", "Unknown"))

        print("\nClaim type:")
        print(analysis.get("claim_type", "Unknown"))

        print("\nVerification questions:")

        for question in analysis.get("verification_questions", []):
            print(f"- {question}")

        search_queries = analysis.get("search_queries", [])

        print("\nGenerated search queries:")

        for query in search_queries:
            print(f"- {query}")

        # ------------------------------------------------------
        # STEP 2: ACADEMIC SEARCH
        # ------------------------------------------------------

        print("\n" + "=" * 60)
        print("[STEP 2] Searching academic publications...")
        print("=" * 60)

        publications = search_multiple_queries(
            search_queries,
            per_page=5
        )

        result["publications"] = publications
        result["total_publications"] = len(publications)

        print(f"\nAcademic publications found: {len(publications)}")

        # ------------------------------------------------------
        # STEP 3: EVIDENCE RETRIEVAL
        # ------------------------------------------------------

        print("\n" + "=" * 60)
        print("[STEP 3] Retrieving publication evidence...")
        print("=" * 60)

        evidence_records = retrieve_evidence(publications)

        result["total_abstracts"] = len(evidence_records)

        print(f"\nEvidence records retrieved: {len(evidence_records)}")

        # Initial evaluation uses a smaller subset.
        # Adaptive research later expands the evidence base.

        initial_evidence = evidence_records[:3]

        print(
            "Publications selected for initial evaluation:",
            len(initial_evidence)
        )

        # ------------------------------------------------------
        # STEP 4: EVIDENCE EVALUATION
        # ------------------------------------------------------

        print("\n" + "=" * 60)
        print("[STEP 4] Evaluating evidence...")
        print("=" * 60)

        evaluated_evidence = evaluate_evidence(
            self.client,
            self.model,
            claim,
            initial_evidence
        )

        result["evaluated_evidence"] = evaluated_evidence

        print(
            "Evidence records evaluated:",
            len(evaluated_evidence)
        )

        # ------------------------------------------------------
        # STEP 4.1: RESEARCH QUALITY
        # ------------------------------------------------------

        print("\n" + "=" * 60)
        print("[STEP 4.1] Assessing research quality and relevance...")
        print("=" * 60)

        evaluated_evidence = evaluate_research_quality(
            self.client,
            self.model,
            claim,
            evaluated_evidence
        )

        result["evaluated_evidence"] = evaluated_evidence

        eligible_evidence = self.get_eligible_evidence(
            evaluated_evidence
        )

        result["eligible_evidence"] = eligible_evidence

        indirect_count = 0
        excluded_count = 0
        quality_failures = 0

        for record in evaluated_evidence:

            quality = record.get("quality_assessment", {})

            if quality.get("status") != "completed":
                quality_failures += 1
                continue

            if quality.get("outcome_alignment") == "indirect":
                indirect_count += 1

            if quality.get("recommendation") == "exclude":
                excluded_count += 1

        print("\nResearch quality summary:")
        print(f"- Publications assessed: {len(evaluated_evidence)}")
        print(f"- Direct eligible evidence: {len(eligible_evidence)}")
        print(f"- Indirect educational evidence: {indirect_count}")
        print(f"- Excluded evidence: {excluded_count}")
        print(f"- Quality assessment failures: {quality_failures}")

        # ------------------------------------------------------
        # STEP 5: INITIAL DECISION
        # ------------------------------------------------------

        print("\n" + "=" * 60)
        print("[STEP 5] Making initial verification decision...")
        print("=" * 60)

        initial_decision = self.make_filtered_decision(
            evaluated_evidence
        )

        result["initial_decision"] = initial_decision
        result["decision"] = initial_decision

        print("\nInitial Verdict:", initial_decision.get("verdict"))
        print("Initial Confidence:", initial_decision.get("confidence"))

        print("\nInitial Explanation:")
        print(initial_decision.get("explanation", "No explanation available."))

        # ------------------------------------------------------
        # STEP 6: SAVE INITIAL VERIFICATION
        # ------------------------------------------------------

        print("\n" + "=" * 60)
        print("[STEP 6] Saving initial verification to memory...")
        print("=" * 60)

        # IMPORTANT:
        # memory.py defines save_claim(claim, decision).
        # Do not pass verdict, confidence and explanation separately.

        claim_id = save_claim(
            claim,
            initial_decision
        )

        result["claim_id"] = claim_id

        save_evidence(
            claim_id,
            evaluated_evidence
        )

        print(f"Initial verification saved with Claim ID: {claim_id}")

        result["status"] = "initial_completed"

        return result

    # ==========================================================
    # USER FEEDBACK
    # ==========================================================

    def collect_feedback(self, result):

        print("\n" + "=" * 60)
        print("[FEEDBACK] User feedback")
        print("=" * 60)

        feedback = input(
            "\nEnter feedback about the verification:\n> "
        ).strip()

        if not feedback:

            print("\nNo feedback provided.")
            return result

        claim_id = result.get("claim_id")

        if claim_id:

            save_feedback(
                claim_id,
                feedback
            )

            print("\nFeedback saved successfully.")

        result["user_feedback"] = feedback

        return result

    # ==========================================================
    # REFLECTION
    # ==========================================================

    def reflect(self, result):

        print("\n" + "=" * 60)
        print("[REFLECTION] Analyzing user feedback...")
        print("=" * 60)

        claim_id = result.get("claim_id")

        if not claim_id:

            print("\nNo claim ID available for reflection.")
            return result

        feedback_records = get_feedback(claim_id)

        if not feedback_records:

            print("\nNo feedback available.")
            return result

        reflection = reflect_on_feedback(
            self.client,
            self.model,
            feedback_records
        )

        result["reflection"] = reflection

        print("\nReflection summary:")
        print(reflection.get("summary", "No summary available."))

        print("\nIdentified concerns:")

        for concern in reflection.get("concerns", []):
            print(f"- {concern}")

        print("\nRecommendations:")

        for recommendation in reflection.get("recommendations", []):
            print(f"- {recommendation}")

        return result

    # ==========================================================
    # ADAPTIVE RESEARCH
    # ==========================================================

    def adapt_research(self, result):

        print("\n" + "=" * 60)
        print("[ADAPTIVE RESEARCH] Starting adaptive research...")
        print("=" * 60)

        reflection = result.get("reflection")

        if not reflection:

            print(
                "\nAdaptive research skipped because "
                "no reflection is available."
            )

            return result

        claim = result.get("claim")

        original_queries = result.get(
            "analysis", {}
        ).get(
            "search_queries", []
        )

        # ------------------------------------------------------
        # Generate adaptive queries
        # ------------------------------------------------------

        
        # ======================================================
        # GENERATE AND VALIDATE ADAPTIVE SEARCH QUERIES
        # ======================================================

        adaptive_response = generate_adaptive_queries(
            self.client,
            self.model,
            claim,
            original_queries,
            reflection
        )

        # The adaptive planner returns a dictionary containing
        # status, reason and new_search_queries.

        if isinstance(adaptive_response, dict):

            new_queries = adaptive_response.get(
                "new_search_queries",
                []
            )

        elif isinstance(adaptive_response, list):

            new_queries = adaptive_response

        else:

            new_queries = []

        # Validate and remove duplicate queries.

        validated_queries = []
        seen_queries = set()

        if isinstance(new_queries, list):

            for query in new_queries:

                if not isinstance(query, str):
                    continue

                query = query.strip()

                if not query:
                    continue

                query_key = query.lower()

                if query_key in seen_queries:
                    continue

                seen_queries.add(query_key)
                validated_queries.append(query)

        result["adaptive_queries"] = validated_queries

        print("\nAdaptive search queries:")

        for query in validated_queries:
            print(f"- {query}")

        if not validated_queries:

            print(
                "\nAdaptive research stopped: "
                "No valid search queries were generated."
            )

            print("Planner response:", adaptive_response)

            return result

        # ------------------------------------------------------
        # Adaptive academic search and retrieval
        # ------------------------------------------------------

        print("\nSearching for additional publications...")

        original_publications = result.get("publications", [])

        adaptive_result = conduct_adaptive_research(
            validated_queries,
            original_publications
        )

        additional_publications = adaptive_result.get(
            "new_publications", []
        )

        additional_evidence = adaptive_result.get(
            "new_evidence", []
        )

        result["additional_publications"] = additional_publications

        print(
            "\nAdditional unique publications found:",
            len(additional_publications)
        )

        print(
            "Additional abstracts retrieved:",
            len(additional_evidence)
        )

        # ------------------------------------------------------
        # Evaluate additional evidence
        # ------------------------------------------------------

        print("\n" + "=" * 60)
        print("[ADAPTIVE RESEARCH] Evaluating additional evidence...")
        print("=" * 60)

        additional_evaluations = []

        if additional_evidence:

            additional_evaluations = evaluate_evidence(
                self.client,
                self.model,
                claim,
                additional_evidence
            )

        # ------------------------------------------------------
        # Assess additional research quality
        # ------------------------------------------------------

        print("\n" + "=" * 60)
        print("[ADAPTIVE RESEARCH] Assessing research quality...")
        print("=" * 60)

        if additional_evaluations:

            additional_evaluations = evaluate_research_quality(
                self.client,
                self.model,
                claim,
                additional_evaluations
            )

        result["additional_evaluations"] = additional_evaluations

        print(
            "Additional publications evaluated:",
            len(additional_evaluations)
        )

        # ------------------------------------------------------
        # Combine original and additional evidence
        # ------------------------------------------------------

        combined_evidence = combine_evaluated_evidence(
            result.get("evaluated_evidence", []),
            additional_evaluations
        )

        result["combined_evidence"] = combined_evidence

        print(
            "\nCombined unique evaluated evidence:",
            len(combined_evidence)
        )

        combined_eligible = self.get_eligible_evidence(
            combined_evidence
        )

        print(
            "Combined eligible direct evidence:",
            len(combined_eligible)
        )

        # ------------------------------------------------------
        # Make adaptive decision
        # ------------------------------------------------------

        print("\n" + "=" * 60)
        print("[ADAPTIVE RESEARCH] Making adaptive decision...")
        print("=" * 60)

        adaptive_decision = self.make_filtered_decision(
            combined_evidence
        )

        result["adaptive_decision"] = adaptive_decision
        result["decision"] = adaptive_decision

        print("\nAdaptive Verdict:", adaptive_decision.get("verdict"))
        print("Adaptive Confidence:", adaptive_decision.get("confidence"))

        print("\nAdaptive Explanation:")
        print(adaptive_decision.get("explanation", "No explanation available."))

        # ------------------------------------------------------
        # Save adaptive result
        # ------------------------------------------------------

        print("\n" + "=" * 60)
        print("[ADAPTIVE RESEARCH] Saving updated verification...")
        print("=" * 60)

        # CORRECTED:
        # save_claim accepts exactly two arguments:
        # claim and decision.

        adaptive_claim_id = save_claim(
            claim,
            adaptive_decision
        )

        result["adaptive_claim_id"] = adaptive_claim_id

        save_evidence(
            adaptive_claim_id,
            combined_evidence
        )

        print(
            f"Adaptive verification saved with Claim ID: "
            f"{adaptive_claim_id}"
        )

        # ------------------------------------------------------
        # STEP 7: QUANTITATIVE EVIDENCE ANALYSIS
        # ------------------------------------------------------

        print("\n" + "=" * 60)
        print("[STEP 7] Analyzing quantitative evidence...")
        print("=" * 60)

        quantitative_evidence = analyze_quantitative_evidence(
            self.client,
            self.model,
            combined_eligible
        )

        result["quantitative_evidence"] = quantitative_evidence
        result["quantitative_status"] = "completed"

        # ------------------------------------------------------
        # Quantitative categories
        # ------------------------------------------------------

        publications_with_numerical_data = [
            record for record in quantitative_evidence
            if record.get(
                "quantitative_assessment", {}
            ).get("has_quantitative_data", False)
        ]

        direct_outcome_publications = [
            record for record in quantitative_evidence
            if record.get(
                "quantitative_assessment", {}
            ).get("has_direct_outcome_statistics", False)
        ]

        indirect_outcome_publications = [
            record for record in quantitative_evidence
            if record.get(
                "quantitative_assessment", {}
            ).get("indirect_outcome_evidence", False)
        ]

        methodology_only_publications = [
            record for record in quantitative_evidence
            if record.get(
                "quantitative_assessment", {}
            ).get("outcome_relevance") == "methodology_only"
        ]

        # ------------------------------------------------------
        # Quantitative summary
        # ------------------------------------------------------

        print("\nQuantitative analysis completed!")

        print(
            "Eligible publications analyzed:",
            len(quantitative_evidence)
        )

        print(
            "Publications with numerical information:",
            len(publications_with_numerical_data)
        )

        print(
            "Publications with direct academic outcome statistics:",
            len(direct_outcome_publications)
        )

        print(
            "Publications with indirect educational outcome statistics:",
            len(indirect_outcome_publications)
        )

        print(
            "Publications with methodology-only statistics:",
            len(methodology_only_publications)
        )

        # ------------------------------------------------------
        # Display quantitative details
        # ------------------------------------------------------

        if publications_with_numerical_data:

            print("\nQuantitative evidence details:")

            for index, record in enumerate(
                publications_with_numerical_data,
                start=1
            ):

                assessment = record.get(
                    "quantitative_assessment", {}
                )

                print("\n" + "-" * 60)
                print(f"Publication {index}")

                print("Title:", record.get("title", "Unknown"))
                print("Year:", record.get("year", "Unknown"))

                print(
                    "Outcome relevance:",
                    assessment.get("outcome_relevance", "Unknown")
                )

                print(
                    "Sample size:",
                    assessment.get("sample_size", "Not reported")
                )

                for field, label in [
                    ("percentages", "Percentages"),
                    ("effect_sizes", "Effect sizes"),
                    ("p_values", "P-values"),
                    ("confidence_intervals", "Confidence intervals"),
                    ("other_statistics", "Other statistics")
                ]:

                    values = assessment.get(field, [])

                    if values:

                        print(f"\n{label}:")

                        for item in values:
                            print(f"- {item}")

                summary = (
                    assessment.get("quantitative_summary")
                    or assessment.get("summary")
                    or "No summary available."
                )

                print("\nSummary:", summary)

        return result

    # ==========================================================
    # FINAL REPORT
    # ==========================================================

    def display_final_report(self, result):

        print("\n\n")
        print("=" * 70)
        print("VERIAGENT - FINAL RESEARCH CLAIM VERIFICATION REPORT")
        print("=" * 70)

        # ------------------------------------------------------
        # Claim
        # ------------------------------------------------------

        print("\nCLAIM")
        print("-" * 70)

        print(result.get("claim", "Unknown"))

        # ------------------------------------------------------
        # Initial decision
        # ------------------------------------------------------

        initial_decision = result.get("initial_decision", {})

        print("\nINITIAL VERIFICATION")
        print("-" * 70)

        print("Verdict:", initial_decision.get("verdict", "Unknown"))
        print("Confidence:", initial_decision.get("confidence", "Unknown"))

        print("\nExplanation:")
        print(
            initial_decision.get(
                "explanation",
                "No explanation available."
            )
        )

        # ------------------------------------------------------
        # Adaptive decision
        # ------------------------------------------------------

        adaptive_decision = result.get("adaptive_decision")

        if adaptive_decision:

            print("\nADAPTIVE VERIFICATION")
            print("-" * 70)

            print(
                "Verdict:",
                adaptive_decision.get("verdict", "Unknown")
            )

            print(
                "Confidence:",
                adaptive_decision.get("confidence", "Unknown")
            )

            print("\nExplanation:")

            print(
                adaptive_decision.get(
                    "explanation",
                    "No explanation available."
                )
            )

        # ------------------------------------------------------
        # Research statistics
        # ------------------------------------------------------

        initial_publications = result.get("publications", [])
        additional_publications = result.get("additional_publications", [])

        evaluated_evidence = result.get("evaluated_evidence", [])
        additional_evaluations = result.get("additional_evaluations", [])

        total_evaluated = (
            len(evaluated_evidence) +
            len(additional_evaluations)
        )

        print("\nRESEARCH STATISTICS")
        print("-" * 70)

        print("Initial publications retrieved:", len(initial_publications))
        print("Additional publications retrieved:", len(additional_publications))

        print(
            "Total publications retrieved:",
            result.get("total_publications", 0) + len(additional_publications)
        )

        print("Total publications evaluated:", total_evaluated)

        print(
            "Total abstracts initially retrieved:",
            result.get("total_abstracts", 0)
        )

        # ------------------------------------------------------
        # Research quality statistics
        # ------------------------------------------------------

        print("\nRESEARCH QUALITY")
        print("-" * 70)

        all_quality_records = (
            evaluated_evidence +
            additional_evaluations
        )

        quality_assessed = 0
        direct_eligible = 0
        indirect_educational = 0
        excluded = 0
        quality_failures = 0

        for record in all_quality_records:

            quality = record.get("quality_assessment", {})

            if quality.get("status") == "completed":
                quality_assessed += 1
            else:
                quality_failures += 1

            if quality.get("eligible_for_decision", False):
                direct_eligible += 1

            if quality.get("outcome_alignment") == "indirect":
                indirect_educational += 1

            if quality.get("recommendation") == "exclude":
                excluded += 1

        print("Publications quality assessed:", quality_assessed)
        print("Direct eligible publications:", direct_eligible)
        print("Indirect educational evidence:", indirect_educational)
        print("Excluded publications:", excluded)
        print("Quality assessment failures:", quality_failures)

        # ------------------------------------------------------
        # Adaptive research statistics
        # ------------------------------------------------------

        print("\nADAPTIVE RESEARCH")
        print("-" * 70)

        print(
            "Adaptive queries generated:",
            len(result.get("adaptive_queries", []))
        )

        print(
            "Additional publications found:",
            len(additional_publications)
        )

        print(
            "Additional publications evaluated:",
            len(additional_evaluations)
        )

        # ------------------------------------------------------
        # Quantitative analysis
        # ------------------------------------------------------

        print("\nQUANTITATIVE EVIDENCE ANALYSIS")
        print("-" * 70)

        quantitative_evidence = result.get("quantitative_evidence", [])

        publications_with_numerical_data = [
            record for record in quantitative_evidence
            if record.get(
                "quantitative_assessment", {}
            ).get("has_quantitative_data", False)
        ]

        direct_outcome_publications = [
            record for record in quantitative_evidence
            if record.get(
                "quantitative_assessment", {}
            ).get("has_direct_outcome_statistics", False)
        ]

        indirect_outcome_publications = [
            record for record in quantitative_evidence
            if record.get(
                "quantitative_assessment", {}
            ).get("indirect_outcome_evidence", False)
        ]

        methodology_only_publications = [
            record for record in quantitative_evidence
            if record.get(
                "quantitative_assessment", {}
            ).get("outcome_relevance") == "methodology_only"
        ]

        print(
            "Quantitative analysis status:",
            result.get("quantitative_status", "Unknown")
        )

        print("Eligible publications analyzed:", len(quantitative_evidence))

        print(
            "Publications with numerical information:",
            len(publications_with_numerical_data)
        )

        print(
            "Publications with direct academic outcome statistics:",
            len(direct_outcome_publications)
        )

        print(
            "Publications with indirect educational outcome statistics:",
            len(indirect_outcome_publications)
        )

        print(
            "Publications with methodology-only statistics:",
            len(methodology_only_publications)
        )

        # ------------------------------------------------------
        # Quantitative details
        # ------------------------------------------------------

        if quantitative_evidence:

            print("\nQUANTITATIVE FINDINGS")

            for index, record in enumerate(
                quantitative_evidence,
                start=1
            ):

                assessment = record.get(
                    "quantitative_assessment", {}
                )

                if not assessment.get("has_quantitative_data", False):
                    continue

                print("\n" + "-" * 70)
                print(f"Publication {index}")

                print("Title:", record.get("title", "Unknown"))
                print("Year:", record.get("year", "Unknown"))

                print(
                    "Outcome relevance:",
                    assessment.get("outcome_relevance", "Unknown")
                )

                print(
                    "Sample size:",
                    assessment.get("sample_size", "Not reported")
                )

                for field, label in [
                    ("percentages", "Percentages"),
                    ("effect_sizes", "Effect sizes"),
                    ("p_values", "P-values"),
                    ("confidence_intervals", "Confidence intervals"),
                    ("other_statistics", "Other statistics")
                ]:

                    values = assessment.get(field, [])

                    if values:

                        print(f"\n{label}:")

                        for item in values:
                            print(f"- {item}")

                summary = (
                    assessment.get("quantitative_summary")
                    or assessment.get("summary")
                    or "No summary available."
                )

                print("\nSummary:", summary)

        # ------------------------------------------------------
        # Final interpretation
        # ------------------------------------------------------

        final_decision = result.get("decision", {})

        print("\nFINAL VERDICT")
        print("-" * 70)

        print(final_decision.get("verdict", "Unknown"))

        print(
            "Confidence:",
            final_decision.get("confidence", "Unknown")
        )

        print("\nFinal interpretation:")

        print(
            final_decision.get(
                "explanation",
                "No explanation available."
            )
        )

        if direct_outcome_publications:

            print("\nQuantitative interpretation:")

            print(
                f"{len(direct_outcome_publications)} eligible "
                "publication(s) contained direct academic outcome statistics."
            )

            print(
                "These statistics provide more direct evidence for the "
                "claim than methodology-only or indirect outcomes such "
                "as motivation and engagement."
            )

        # ------------------------------------------------------
        # Memory
        # ------------------------------------------------------

        print("\nMEMORY")
        print("-" * 70)

        print("Initial claim ID:", result.get("claim_id", "Not available"))

        print(
            "Adaptive claim ID:",
            result.get("adaptive_claim_id", "Not available")
        )

        # ------------------------------------------------------
        # Limitations
        # ------------------------------------------------------

        print("\nLIMITATIONS")
        print("-" * 70)

        limitations = [
            "VeriAgent provides a preliminary research assessment "
            "rather than a definitive scientific conclusion.",

            "The system depends on the publications retrieved "
            "from the academic search process.",

            "Much of the evidence evaluation is based on publication "
            "abstracts rather than complete papers.",

            "AI-assisted research quality and evidence classification "
            "may contain errors.",

            "The decision engine uses a project-defined heuristic "
            "rather than an established scientific meta-analytic rule.",

            "Quantitative statistics should be checked against the "
            "original publications before being treated as definitive."
        ]

        for index, limitation in enumerate(limitations, start=1):
            print(f"{index}. {limitation}")

        print("\n" + "=" * 70)
        print("VERIAGENT VERIFICATION COMPLETED")
        print("=" * 70)


# ==============================================================
# MAIN PROGRAM
# ==============================================================

def main():

    print("\n" + "=" * 60)
    print("VERIAGENT - RESEARCH CLAIM VERIFICATION")
    print("=" * 60)

    claim = input(
        "\nEnter a research claim to verify:\n> "
    ).strip()

    if not claim:

        print("\nNo claim entered. Exiting.")
        return

    agent = VeriAgent()

    # ----------------------------------------------------------
    # Initial verification
    # ----------------------------------------------------------

    result = agent.verify_claim(claim)

    if result.get("status") == "error":

        print("\nVerification failed:")
        print(result.get("message", "Unknown error."))
        return

    # ----------------------------------------------------------
    # User feedback
    # ----------------------------------------------------------

    result = agent.collect_feedback(result)

    # ----------------------------------------------------------
    # Reflection
    # ----------------------------------------------------------

    result = agent.reflect(result)

    # ----------------------------------------------------------
    # Adaptive research
    # ----------------------------------------------------------

    result = agent.adapt_research(result)

    # ----------------------------------------------------------
    # Final report
    # ----------------------------------------------------------

    agent.display_final_report(result)


if __name__ == "__main__":
    main()
