
import json
import re
import time


def extract_json(response_text):
    """
    Extract JSON returned by Gemini.
    Handles Markdown code fences.
    """

    if not response_text:
        raise ValueError("Gemini returned an empty response.")

    cleaned = response_text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(r"\s*```$", "", cleaned)

    return json.loads(cleaned)


def create_failed_assessment(error):
    """
    Return a consistent assessment when evaluation fails.
    """

    return {
        "status": "failed",
        "relevance_score": 0,
        "relevance_level": "unknown",
        "outcome_alignment": "unknown",
        "technology_alignment": "unknown",
        "claim_scope": "unclear",
        "technology_category": "unknown",
        "study_type": "unknown",
        "evidence_directness": "unknown",
        "quality_level": "unknown",
        "recommendation": "review_cautiously",
        "eligible_for_decision": False,
        "matched_outcomes": [],
        "matched_technologies": [],
        "study_design_details": [],
        "reasoning": "The publication could not be assessed.",
        "limitations": [str(error)]
    }


def assess_publication_quality(
    client,
    model,
    claim,
    evidence_record
):
    """
    Assess publication relevance, technology alignment,
    outcome alignment, and preliminary research quality.

    Uses only the publication title and abstract.
    """

    title = (
        evidence_record.get("title")
        or "Title unavailable"
    )

    abstract = evidence_record.get("abstract")

    if not abstract:

        return {
            "status": "completed",
            "relevance_score": 0,
            "relevance_level": "very_low",
            "outcome_alignment": "unknown",
            "technology_alignment": "unknown",
            "claim_scope": "unclear",
            "technology_category": "unknown",
            "study_type": "unknown",
            "evidence_directness": "unknown",
            "quality_level": "unknown",
            "recommendation": "exclude",
            "eligible_for_decision": False,
            "matched_outcomes": [],
            "matched_technologies": [],
            "study_design_details": [],
            "reasoning": (
                "No abstract is available for assessment."
            ),
            "limitations": [
                "Abstract unavailable"
            ]
        }

    prompt = f"""
You are the research relevance and evidence applicability
evaluator of VeriAgent.

Your task is to assess whether a research publication
provides useful evidence for the EXACT research claim.

RESEARCH CLAIM:
{claim}

PUBLICATION TITLE:
{title}

PUBLICATION ABSTRACT:
{abstract[:7000]}


IMPORTANT: EVALUATE FOUR SEPARATE DIMENSIONS.

DIMENSION 1: OUTCOME ALIGNMENT

Does the publication measure the outcome in the claim?

For a claim about student academic performance:

DIRECT outcomes:
- Examination scores
- Academic grades
- Standardized test scores
- Learning achievement
- Knowledge acquisition
- Learning gains
- Academic attainment

INDIRECT outcomes:
- Student engagement
- Motivation
- Satisfaction
- Learning attitudes
- Anxiety
- Technology acceptance
- Self-efficacy

UNRELATED:
- Healthcare outcomes
- Cardiovascular outcomes
- Business performance
- Other outcomes unrelated to student learning.

Do not classify satisfaction or engagement as direct
academic performance.


DIMENSION 2: TECHNOLOGY ALIGNMENT

Identify the technology investigated in the publication.

Possible categories include:

- generative_ai
- ai_chatbot
- intelligent_tutoring_system
- machine_learning
- educational_robotics
- adaptive_learning_ai
- general_ai
- non_ai_technology
- other
- unknown

Compare the publication's technology with the technology
scope of the research claim.

technology_alignment must be:

- direct: The publication investigates the same
  technology or a clearly matching AI intervention.

- related: It investigates a different but relevant
  AI technology.

- unrelated: It does not investigate a technology
  relevant to the claim.

- unknown: The abstract does not provide enough information.

IMPORTANT EXAMPLE:

If the claim is broadly about artificial intelligence
in education, educational robotics may be related evidence.

If the claim specifically concerns generative AI chatbots,
educational robotics should normally be considered unrelated
or insufficiently aligned.

Do not assume all AI technologies have identical effects.


DIMENSION 3: CLAIM SCOPE

Identify the technology scope of the submitted claim.

Use:

- broad_ai: The claim concerns AI generally or multiple
  AI technologies.

- specific_ai: The claim identifies a particular AI
  technology or intervention.

- unclear: The technology scope cannot be established.

Do not narrow or broaden the user's claim artificially.


DIMENSION 4: RESEARCH DESIGN AND QUALITY

Identify the research design when explicitly described.

Allowed study types:

- randomized_controlled_trial
- quasi_experimental
- observational_study
- systematic_review
- meta_analysis
- literature_review
- theoretical
- conceptual
- other
- unknown

Assess preliminary quality based on information available
in the abstract.

Consider:
- Whether the research design is described.
- Whether the population is identified.
- Whether outcomes are clearly measured.
- Whether methods and findings are sufficiently reported.
- Whether limitations are acknowledged.

Do not assume a study is high quality simply because
it is a randomized trial or meta-analysis.

Do not invent sample sizes, findings, or research methods.

A title and abstract cannot establish the full quality
of a publication. Explicitly acknowledge this limitation.


RECOMMENDATION:

include:
Relevant technology and direct alignment with the
claimed outcome, with sufficient information in the abstract.

review_cautiously:
Related technology, unclear methods, indirect outcomes,
or incomplete information.

exclude:
Unrelated technology or unrelated research outcomes.


RELEVANCE SCORING:

90-100: Highly relevant to the exact claim.
70-89: Relevant, with some limitations.
40-69: Partially relevant or related.
20-39: Weak relevance.
0-19: Unrelated.

Use a whole number from 0 to 100.


RETURN ONLY VALID JSON:

{{
    "relevance_score": 85,
    "relevance_level": "high",
    "claim_scope": "broad_ai",
    "technology_category": "ai_chatbot",
    "technology_alignment": "direct",
    "outcome_alignment": "direct",
    "study_type": "randomized_controlled_trial",
    "evidence_directness": "direct",
    "quality_level": "moderate",
    "recommendation": "include",
    "matched_outcomes": [
        "Examination scores"
    ],
    "matched_technologies": [
        "AI chatbot"
    ],
    "study_design_details": [
        "Randomized controlled trial, if explicitly reported"
    ],
    "reasoning": "Explain the relevance and limitations.",
    "limitations": [
        "Assessment based on abstract only."
    ]
}}

The above values are examples only.
Do not copy them unless supported by the supplied abstract.

ALLOWED VALUES:

relevance_level:
high, medium, low, very_low

claim_scope:
broad_ai, specific_ai, unclear

technology_alignment:
direct, related, unrelated, unknown

outcome_alignment:
direct, indirect, unrelated, unknown

technology_category:
generative_ai, ai_chatbot, intelligent_tutoring_system,
machine_learning, educational_robotics,
adaptive_learning_ai, general_ai,
non_ai_technology, other, unknown

study_type:
randomized_controlled_trial, quasi_experimental,
observational_study, systematic_review, meta_analysis,
literature_review, theoretical, conceptual, other, unknown

evidence_directness:
direct, indirect, background, unknown

quality_level:
high, moderate, low, unknown

recommendation:
include, review_cautiously, exclude

Be conservative.
Do not confuse technology relevance with outcome relevance.
Do not treat an AI-related title as proof of academic improvement.
Return only valid JSON.
"""

    try:

        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        assessment = extract_json(response.text)

        if not isinstance(assessment, dict):
            raise ValueError("Invalid assessment format.")

        # Validate numerical relevance score.
        score = assessment.get("relevance_score", 0)

        if isinstance(score, bool) or not isinstance(
            score, (int, float)
        ):
            score = 0

        score = max(0, min(100, int(score)))

        assessment["relevance_score"] = score

        # Validate allowed categories.
        allowed_values = {
            "relevance_level": {
                "high", "medium", "low", "very_low"
            },
            "claim_scope": {
                "broad_ai", "specific_ai", "unclear"
            },
            "technology_alignment": {
                "direct", "related", "unrelated", "unknown"
            },
            "outcome_alignment": {
                "direct", "indirect", "unrelated", "unknown"
            },
            "technology_category": {
                "generative_ai",
                "ai_chatbot",
                "intelligent_tutoring_system",
                "machine_learning",
                "educational_robotics",
                "adaptive_learning_ai",
                "general_ai",
                "non_ai_technology",
                "other",
                "unknown"
            },
            "study_type": {
                "randomized_controlled_trial",
                "quasi_experimental",
                "observational_study",
                "systematic_review",
                "meta_analysis",
                "literature_review",
                "theoretical",
                "conceptual",
                "other",
                "unknown"
            },
            "evidence_directness": {
                "direct", "indirect", "background", "unknown"
            },
            "quality_level": {
                "high", "moderate", "low", "unknown"
            },
            "recommendation": {
                "include", "review_cautiously", "exclude"
            }
        }

        for field, valid_values in allowed_values.items():

            if assessment.get(field) not in valid_values:

                assessment[field] = "unknown"

        # Ensure list fields have consistent formats.
        list_fields = [
            "matched_outcomes",
            "matched_technologies",
            "study_design_details",
            "limitations"
        ]

        for field in list_fields:

            if not isinstance(assessment.get(field), list):
                assessment[field] = []

        if not assessment.get("reasoning"):

            assessment["reasoning"] = (
                "No reasoning was provided."
            )

        # -------------------------------------------------
        # DETERMINISTIC ELIGIBILITY CHECK
        # -------------------------------------------------

        # A publication must measure the actual claimed outcome.
        direct_outcome = (
            assessment["outcome_alignment"] == "direct"
            and assessment["evidence_directness"] == "direct"
        )

        # The technology must match the claim.
        direct_technology = (
            assessment["technology_alignment"] == "direct"
        )

        related_broad_technology = (
            assessment["technology_alignment"] == "related"
            and assessment["claim_scope"] == "broad_ai"
        )

        technology_matches = (
            direct_technology or related_broad_technology
        )

        # The recommendation and relevance score must also qualify.
        eligible = (
            assessment["recommendation"] == "include"
            and direct_outcome
            and technology_matches
            and score >= 70
        )

        # Do not allow unrelated outcomes or technology
        # to enter the main decision.
        if assessment["outcome_alignment"] == "unrelated":
            assessment["recommendation"] = "exclude"

        elif assessment["technology_alignment"] == "unrelated":
            assessment["recommendation"] = "exclude"

        elif not eligible and assessment["recommendation"] == "include":
            assessment["recommendation"] = "review_cautiously"

        assessment["eligible_for_decision"] = (
            eligible
            and assessment["recommendation"] == "include"
        )

        assessment["status"] = "completed"

        # Add an explicit limitation about abstract-based assessment.
        if "Assessment based on title and abstract only." not in assessment["limitations"]:

            assessment["limitations"].append(
                "Assessment based on title and abstract only."
            )

        return assessment

    except Exception as error:

        return create_failed_assessment(error)


def evaluate_research_quality(
    client,
    model,
    claim,
    evidence_records
):
    """
    Evaluate all publications and attach quality assessments
    to their corresponding evidence records.
    """

    if not isinstance(evidence_records, list):

        raise ValueError(
            "Evidence records must be provided as a list."
        )

    evaluated_records = []

    total = len(evidence_records)

    for index, record in enumerate(
        evidence_records,
        start=1
    ):

        print(
            f"\nAssessing publication quality {index}/{total}..."
        )

        start_time = time.time()

        assessment = assess_publication_quality(
            client,
            model,
            claim,
            record
        )

        record["quality_assessment"] = assessment

        elapsed = time.time() - start_time

        print(
            f"Assessment completed in {elapsed:.2f} seconds"
        )

        print(
            "Relevance score:",
            assessment.get("relevance_score")
        )

        print(
            "Technology category:",
            assessment.get("technology_category")
        )

        print(
            "Technology alignment:",
            assessment.get("technology_alignment")
        )

        print(
            "Outcome alignment:",
            assessment.get("outcome_alignment")
        )

        print(
            "Recommendation:",
            assessment.get("recommendation")
        )

        print(
            "Eligible for decision:",
            assessment.get("eligible_for_decision")
        )

        evaluated_records.append(record)

    return evaluated_records
