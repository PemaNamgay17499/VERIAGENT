
import json
import re
import time


def extract_json(response_text):
    """
    Safely extract JSON from Gemini responses.
    """

    if not response_text or not response_text.strip():
        raise ValueError("Gemini returned an empty response.")

    result = response_text.strip()

    result = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        result,
        flags=re.IGNORECASE
    )

    return json.loads(result)

def evaluate_evidence(client, model, claim, evidence_records):
    """
    Evaluate research abstracts against a submitted claim.

    Each publication receives:
    - Evidence classification
    - Explanation
    - Relevance
    - Research design
    - Findings status
    - Evidence strength
    """

    evaluated_records = []

    total = len(evidence_records)

    for number, record in enumerate(evidence_records, start=1):

        print(f"\nEvaluating publication {number}/{total}...")

        start_time = time.time()

        abstract = record.get("abstract")

        # Handle publications without abstracts
        if not abstract or not str(abstract).strip():

            record["evidence_available"] = False

            record["evidence_assessment"] = {
                "classification": "insufficient",
                "explanation": (
                    "The publication does not contain an available "
                    "abstract. Its research findings cannot be "
                    "evaluated, so it is excluded from evidence-based "
                    "decision scoring."
                ),
                "relevance": "low",
                "study_type": "unknown",
                "findings_status": "not_available",
                "evidence_strength": "none"
            }

            evaluated_records.append(record)

            print(
                f"Publication {number}/{total}: "
                "Insufficient evidence (abstract unavailable)."
            )

            continue

        # Limit abstract length
        max_abstract_length = 5000

        if len(abstract) > max_abstract_length:
            abstract = abstract[:max_abstract_length] + "..."

        # Gemini evaluation prompt
        prompt = f"""
You are the research evidence evaluation component of VeriAgent.

Your task is to carefully evaluate a research publication
against a submitted research claim.

RESEARCH CLAIM:
{claim}

PUBLICATION TITLE:
{record.get("title")}

PUBLICATION YEAR:
{record.get("year")}

PUBLICATION ABSTRACT:
{abstract}


TASK 1: IDENTIFY THE RESEARCH DESIGN

Identify the most appropriate research design:

- empirical_study
- systematic_review
- meta_analysis
- literature_review
- theoretical_proposal
- conceptual_framework
- other
- unknown

Do not assume a publication is an empirical study simply
because it discusses research or proposes a framework.


TASK 2: IDENTIFY THE FINDINGS STATUS

Classify the findings as exactly one of:

- actual_positive_findings
- actual_negative_findings
- mixed_findings
- proposed_benefits
- no_clear_findings

Use actual_positive_findings or actual_negative_findings
only when the abstract reports findings from completed research.

A proposed framework or expected benefit is not an actual
research finding.


TASK 3: EVALUATE THE EVIDENCE

Classify the evidence into exactly ONE category:

supporting:
The abstract reports actual findings that directly support
the research claim.

contradicting:
The abstract reports actual findings that directly conflict
with the research claim.

neutral:
The findings are mixed, conditional, weak, indirect,
context-dependent, or based only on proposed benefits.
Use this category when the publication discusses a potentially
useful approach but does not demonstrate actual improvement.

insufficient:
The abstract is irrelevant, unavailable, or does not provide
enough information to evaluate the claim.


TASK 4: RATE THE RELEVANCE

Choose exactly one:

- high
- medium
- low

High:
The publication directly investigates the research claim.

Medium:
The publication investigates a related topic but does not
directly measure the main outcome.

Low:
The publication has limited relevance to the claim.


TASK 5: RATE THE EVIDENCE STRENGTH

Choose exactly one:

- high
- medium
- low
- none

High:
The abstract reports clear and directly relevant findings
from a substantial research design, such as a meta-analysis
or well-designed empirical study. Do not infer methodological
quality that is not described.

Medium:
The abstract reports relevant actual findings, but the
evidence has limitations or incomplete detail.

Low:
The evidence is indirect, limited, preliminary, or weak.

None:
There are no usable findings or the abstract is unavailable.


IMPORTANT RULES:

1. Use ONLY the supplied publication information and abstract.
2. Never invent research findings, statistics, or citations.
3. Do not assume correlation proves causation.
4. Do not treat a proposed framework as proven evidence.
5. Do not treat a single publication as proof of a broad claim.
6. Do not classify a publication as supporting simply because
   it mentions positive benefits of artificial intelligence.
7. Distinguish actual research results from expected outcomes.
8. If the findings are mixed or conditional, prefer neutral.
9. Evaluate the publication against the specific claim, not
   merely its general topic.
10. Be cautious when the abstract does not provide enough detail.


RETURN ONLY VALID JSON:

{{
    "classification": "supporting",
    "explanation": "Explain how the reported findings relate to the claim.",
    "relevance": "high",
    "study_type": "empirical_study",
    "findings_status": "actual_positive_findings",
    "evidence_strength": "medium"
}}
"""

        try:

            # Send evaluation request to Gemini
            response = client.interactions.create(
                model=model,
                input=prompt
            )

            result = response.output_text.strip()

            # Convert Gemini response into a Python dictionary
            assessment = extract_json(result)

            # Validate classification
            valid_classifications = [
                "supporting",
                "contradicting",
                "neutral",
                "insufficient"
            ]

            if assessment.get("classification") not in valid_classifications:
                raise ValueError(
                    "Invalid evidence classification."
                )

            # Validate relevance
            valid_relevance = [
                "high",
                "medium",
                "low"
            ]

            if assessment.get("relevance") not in valid_relevance:
                assessment["relevance"] = "low"

            # Validate research design
            valid_study_types = [
                "empirical_study",
                "systematic_review",
                "meta_analysis",
                "literature_review",
                "theoretical_proposal",
                "conceptual_framework",
                "other",
                "unknown"
            ]

            if assessment.get("study_type") not in valid_study_types:
                assessment["study_type"] = "unknown"

            # Validate findings status
            valid_findings_status = [
                "actual_positive_findings",
                "actual_negative_findings",
                "mixed_findings",
                "proposed_benefits",
                "no_clear_findings"
            ]

            if assessment.get("findings_status") not in valid_findings_status:
                assessment["findings_status"] = "no_clear_findings"

            # Validate evidence strength
            valid_strength = [
                "high",
                "medium",
                "low",
                "none"
            ]

            if assessment.get("evidence_strength") not in valid_strength:
                assessment["evidence_strength"] = "low"

            # Ensure explanation exists
            if not assessment.get("explanation"):
                assessment["explanation"] = (
                    "No explanation was provided by the AI evaluator."
                )

            # Store assessment in the original publication record
            record["evidence_assessment"] = assessment

        except Exception as error:

            # Prevent one failed request from stopping all evaluations
            record["evidence_assessment"] = {
                "classification": "insufficient",
                "explanation": (
                    "The publication could not be evaluated because "
                    "the AI evaluation request failed."
                ),
                "relevance": "low",
                "study_type": "unknown",
                "findings_status": "no_clear_findings",
                "evidence_strength": "none"
            }

            print(f"Evaluation error: {error}")

        evaluated_records.append(record)

        elapsed = time.time() - start_time

        print(
            f"Evaluated publication {number}/{total} "
            f"in {elapsed:.2f} seconds"
        )

    return evaluated_records
