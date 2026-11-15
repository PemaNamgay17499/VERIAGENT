
def calculate_evidence_weight(assessment):
    """
    Calculate the weight of an individual publication.

    Weight depends on:
    1. Relevance to the claim
    2. Evidence strength
    3. Research design
    """

    relevance_weights = {
        "high": 1.0,
        "medium": 0.6,
        "low": 0.25
    }

    strength_weights = {
        "high": 1.0,
        "medium": 0.7,
        "low": 0.4,
        "none": 0.0
    }

    study_weights = {
        "meta_analysis": 1.15,
        "systematic_review": 1.10,
        "empirical_study": 1.0,
        "literature_review": 0.75,
        "other": 0.75,
        "theoretical_proposal": 0.6,
        "conceptual_framework": 0.6,
        "unknown": 0.5
    }

    relevance = relevance_weights.get(
        assessment.get("relevance", "low"),
        0.25
    )

    strength = strength_weights.get(
        assessment.get("evidence_strength", "none"),
        0.0
    )

    study_type = study_weights.get(
        assessment.get("study_type", "unknown"),
        0.5
    )

    return relevance * strength * study_type


def make_claim_decision(evaluated_evidence):
    """
    Analyze evaluated publications and determine
    the overall research claim verdict.

    Possible verdicts:
    - Supported
    - Partially Supported
    - Contradicted
    - Inconclusive
    """

    if not evaluated_evidence:
        return {
            "verdict": "Inconclusive",
            "confidence": "Low",
            "explanation": (
                "No evaluated research publications "
                "are available to determine the claim."
            ),
            "statistics": {},
            "limitations": [
                "No research evidence was available."
            ]
        }

    # Initialize evidence scores
    scores = {
        "supporting": 0.0,
        "contradicting": 0.0,
        "neutral": 0.0
    }

    counts = {
        "supporting": 0,
        "contradicting": 0,
        "neutral": 0,
        "insufficient": 0
    }

    limitations = []

    usable_count = 0

    # STEP 1: Examine each publication
    for record in evaluated_evidence:

        assessment = record.get(
            "evidence_assessment",
            {}
        )

        classification = assessment.get(
            "classification",
            "insufficient"
        )

        if classification not in counts:
            classification = "insufficient"

        counts[classification] += 1

        # Exclude insufficient evidence.
        if classification == "insufficient":
            continue

        # Exclude publications that failed research quality assessment.
        quality = record.get("quality_assessment", {})

        if not quality.get("eligible_for_decision", False):
            continue

        # Exclude publications with no usable evidence strength.
        if assessment.get("evidence_strength") == "none":
            continue

        weight = calculate_evidence_weight(assessment)

        if weight <= 0:
            continue

        scores[classification] += weight

        usable_count += 1

        if assessment.get("relevance") == "low":
            limitations.append(
                "Some publications have low relevance "
                "to the submitted claim."
            )

        if assessment.get("findings_status") == "mixed_findings":
            limitations.append(
                "Some publications report mixed research findings."
            )

        if assessment.get("findings_status") == "proposed_benefits":
            limitations.append(
                "Some publications discuss proposed benefits "
                "rather than actual research findings."
            )

    # STEP 2: Calculate total usable evidence
    total_weight = sum(scores.values())

    supporting_score = scores["supporting"]
    contradicting_score = scores["contradicting"]
    neutral_score = scores["neutral"]

    if total_weight == 0:

        return {
            "verdict": "Inconclusive",
            "confidence": "Low",
            "explanation": (
                "The available publications do not provide "
                "sufficient usable evidence to evaluate the claim."
            ),
            "statistics": {
                "publication_counts": counts,
                "weighted_scores": scores
            },
            "limitations": [
                "No publications provided usable evidence."
            ]
        }

    # STEP 3: Calculate evidence proportions
    supporting_ratio = supporting_score / total_weight
    contradicting_ratio = contradicting_score / total_weight
    neutral_ratio = neutral_score / total_weight

    # STEP 4: Determine the overall verdict
    if supporting_ratio >= 0.70:

        verdict = "Supported"

        explanation = (
            "The evaluated research evidence predominantly "
            "supports the submitted claim. However, this "
            "conclusion is limited to the publications retrieved "
            "and evaluated."
        )

    elif contradicting_ratio >= 0.70:

        verdict = "Contradicted"

        explanation = (
            "The evaluated research evidence predominantly "
            "conflicts with the submitted claim. However, "
            "the conclusion is limited to the publications "
            "retrieved and evaluated."
        )

    elif supporting_ratio >= 0.50 and contradicting_ratio < 0.30:

        verdict = "Partially Supported"

        explanation = (
            "The available evidence leans towards supporting "
            "the claim, but the findings are not sufficiently "
            "consistent or strong to establish full support."
        )

    else:

        verdict = "Inconclusive"

        explanation = (
            "The available research evidence is mixed, "
            "limited, or insufficient to establish a clear "
            "conclusion about the submitted claim."
        )

    if usable_count >= 10 and total_weight >= 5:
        confidence = "High"

    elif usable_count >= 5 and total_weight >= 2:
        confidence = "Medium"

    else:
        confidence = "Low"

    # STEP 6: Remove duplicate limitations
    limitations = list(dict.fromkeys(limitations))

    if counts["insufficient"] > 0:
        limitations.append(
            "Some publications could not provide usable evidence."
        )

    if usable_count < 5:
        limitations.append(
            "The number of evaluated publications is limited."
        )

    if not limitations:
        limitations.append(
            "The decision is based on available abstracts "
            "and AI-assisted evidence assessments."
        )

    # STEP 7: Prepare final decision
    decision = {
        "verdict": verdict,
        "confidence": confidence,
        "explanation": explanation,

        "statistics": {
            "publication_counts": counts,
            "weighted_scores": scores,
            "evidence_proportions": {
                "supporting": round(supporting_ratio, 3),
                "contradicting": round(contradicting_ratio, 3),
                "neutral": round(neutral_ratio, 3)
            },
            "total_usable_publications": usable_count
        },

        "limitations": limitations
    }

    return decision
