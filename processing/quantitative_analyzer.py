
import json
import re


def extract_json(response_text):
    """Extract valid JSON returned by Gemini."""

    if not response_text or not response_text.strip():
        raise ValueError("Gemini returned an empty response.")

    result = response_text.strip()

    result = re.sub(
        r"^```(?:json)?\s*",
        "",
        result,
        flags=re.IGNORECASE
    )

    result = re.sub(r"\s*```$", "", result)

    return json.loads(result)


def create_empty_assessment(error_message=None):
    """Create a consistent empty assessment."""

    return {
        "has_quantitative_data": False,
        "has_direct_outcome_statistics": False,
        "outcome_relevance": "unknown",
        "sample_size": None,
        "study_characteristics": [],
        "methodology_statistics": [],
        "outcome_statistics": [],
        "direct_outcome_evidence": [],
        "indirect_outcome_evidence": [],
        "percentages": [],
        "effect_sizes": [],
        "p_values": [],
        "confidence_intervals": [],
        "other_statistics": [],
        "quantitative_summary": (
            "Quantitative analysis could not be completed."
            if error_message
            else "No quantitative information was identified."
        ),
        "limitations": [error_message] if error_message else []
    }


def extract_sample_size_from_abstract(abstract):
    """
    Extract an explicitly reported participant sample size.

    Uses the original abstract as a fallback when Gemini
    does not populate the structured sample_size field.

    Avoids interpreting percentages, study counts and
    article counts as participant sample sizes.
    """

    if not isinstance(abstract, str) or not abstract.strip():
        return None

    patterns = [
        # Sample of 200 students / sample size was 120 participants
        (
            r"\b(?:sample|sample size)\s+"
            r"(?:of|was|is|=)\s*"
            r"(\d[\d,]*)\s*"
            r"(students|participants|respondents|subjects|learners)?\b"
        ),

        # n=64 / N = 120
        (
            r"\b[nN]\s*=\s*(\d[\d,]*)\b"
        ),

        # 64 undergraduate students / 120 respondents
        (
            r"\b(\d[\d,]*)\s+"
            r"(?:(?:undergraduate|graduate|university|college|"
            r"first-year|second-year|third-year)\s+)*"
            r"(students|participants|respondents|subjects|learners)\b"
        )
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            abstract,
            flags=re.IGNORECASE
        )

        if match:

            value = int(match.group(1).replace(",", ""))

            if value <= 0:
                continue

            unit = (
                match.group(2)
                if len(match.groups()) >= 2 and match.group(2)
                else "participants"
            )

            return {
                "value": value,
                "unit": unit.lower(),
                "source": "abstract"
            }

    return None


def describe_evidence_item(item):
    """Convert an extracted statistic into readable text."""

    if isinstance(item, dict):

        value = item.get("value")
        measure = item.get("measure")
        description = item.get("description")
        context = item.get("context")

        parts = []

        if value is not None:
            parts.append(str(value))

        if measure:
            parts.append(str(measure))

        elif description:
            parts.append(str(description))

        if context:
            parts.append(str(context))

        return " — ".join(parts)

    return str(item)


def generate_fallback_summary(assessment):
    """
    Generate a cautious summary from extracted information
    when Gemini does not provide a usable summary.
    """

    relevance = assessment.get(
        "outcome_relevance",
        "unknown"
    )

    direct = assessment.get(
        "direct_outcome_evidence",
        []
    )

    indirect = assessment.get(
        "indirect_outcome_evidence",
        []
    )

    methodology = assessment.get(
        "methodology_statistics",
        []
    )

    sample_size = assessment.get("sample_size")

    sentences = []

    if relevance == "mixed":

        sentences.append(
            "The abstract reports both direct academic "
            "outcome evidence and indirect educational outcomes."
        )

    elif relevance == "direct_outcome":

        sentences.append(
            "The abstract reports numerical information "
            "related to direct academic outcomes."
        )

    elif relevance == "indirect_outcome":

        sentences.append(
            "The abstract reports indirect educational "
            "outcomes rather than direct academic achievement."
        )

    elif relevance == "methodology_only":

        sentences.append(
            "The abstract reports research methodology "
            "statistics but no direct academic performance statistics."
        )

    elif relevance == "no_outcome_statistics":

        sentences.append(
            "The abstract contains numerical study information "
            "but does not provide identifiable outcome statistics."
        )

    else:

        sentences.append(
            "The available abstract does not provide enough "
            "information to establish a clear quantitative outcome."
        )

    if sample_size:

        value = sample_size.get("value")
        unit = sample_size.get("unit", "participants")

        if value is not None:

            sentences.append(
                f"The reported sample size is {value} {unit}."
            )

    if direct:

        examples = [
            describe_evidence_item(item)
            for item in direct[:2]
        ]

        sentences.append(
            "Direct academic outcome findings reported: "
            + "; ".join(examples)
            + "."
        )

    if indirect:

        examples = [
            describe_evidence_item(item)
            for item in indirect[:2]
        ]

        sentences.append(
            "Indirect educational findings reported: "
            + "; ".join(examples)
            + "."
        )

    if methodology and not direct:

        sentences.append(
            "Methodology statistics should not be interpreted "
            "as evidence of improved student academic performance."
        )

    return " ".join(sentences)


def normalize_assessment(assessment, abstract=None):
    """
    Validate Gemini's assessment and enforce consistent
    outcome classifications.

    Extracts sample size from the original abstract if
    Gemini fails to provide a structured sample size.
    """

    if not isinstance(assessment, dict):

        raise ValueError("Invalid assessment format.")

    list_fields = [
        "study_characteristics",
        "methodology_statistics",
        "outcome_statistics",
        "direct_outcome_evidence",
        "indirect_outcome_evidence",
        "percentages",
        "effect_sizes",
        "p_values",
        "confidence_intervals",
        "other_statistics",
        "limitations"
    ]

    for field in list_fields:

        if not isinstance(assessment.get(field), list):

            assessment[field] = []

    valid_relevance = {
        "direct_outcome",
        "indirect_outcome",
        "methodology_only",
        "mixed",
        "no_outcome_statistics",
        "unknown"
    }

    if assessment.get("outcome_relevance") not in valid_relevance:

        assessment["outcome_relevance"] = "unknown"

    # -------------------------------------------------
    # NORMALIZE SAMPLE SIZE
    # -------------------------------------------------

    sample_size = assessment.get("sample_size")

    if isinstance(sample_size, (int, float)) and sample_size > 0:

        assessment["sample_size"] = {
            "value": int(sample_size),
            "unit": "participants"
        }

    elif isinstance(sample_size, dict):

        value = sample_size.get("value")

        if (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and value > 0
        ):

            assessment["sample_size"] = {
                "value": int(value),
                "unit": sample_size.get(
                    "unit",
                    "participants"
                ),
                **(
                    {"source": sample_size["source"]}
                    if sample_size.get("source")
                    else {}
                )
            }

        else:

            assessment["sample_size"] = None

    else:

        assessment["sample_size"] = None

    # -------------------------------------------------
    # EXTRACT SAMPLE SIZE FROM ORIGINAL ABSTRACT
    # -------------------------------------------------

    if assessment["sample_size"] is None:

        extracted_sample_size = extract_sample_size_from_abstract(
            abstract
        )

        if extracted_sample_size is not None:

            assessment["sample_size"] = extracted_sample_size

    # -------------------------------------------------
    # DETERMINE WHETHER NUMERICAL INFORMATION EXISTS
    # -------------------------------------------------

    has_data = any([
        assessment["sample_size"] is not None,
        bool(assessment["study_characteristics"]),
        bool(assessment["methodology_statistics"]),
        bool(assessment["outcome_statistics"]),
        bool(assessment["direct_outcome_evidence"]),
        bool(assessment["indirect_outcome_evidence"]),
        bool(assessment["percentages"]),
        bool(assessment["effect_sizes"]),
        bool(assessment["p_values"]),
        bool(assessment["confidence_intervals"]),
        bool(assessment["other_statistics"])
    ])

    assessment["has_quantitative_data"] = bool(has_data)

    # -------------------------------------------------
    # ENFORCE OUTCOME CLASSIFICATION
    # -------------------------------------------------

    has_direct = bool(
        assessment["direct_outcome_evidence"]
    )

    has_indirect = bool(
        assessment["indirect_outcome_evidence"]
    )

    has_methodology = bool(
        assessment["methodology_statistics"]
    )

    if has_direct and has_indirect:

        assessment["outcome_relevance"] = "mixed"

    elif has_direct:

        assessment["outcome_relevance"] = "direct_outcome"

    elif has_indirect:

        assessment["outcome_relevance"] = "indirect_outcome"

    elif has_methodology:

        assessment["outcome_relevance"] = "methodology_only"

    elif has_data:

        assessment["outcome_relevance"] = "no_outcome_statistics"

    else:

        assessment["outcome_relevance"] = "unknown"

    assessment["has_direct_outcome_statistics"] = has_direct

    # -------------------------------------------------
    # VALIDATE SUMMARY
    # -------------------------------------------------

    summary = assessment.get("quantitative_summary")

    if not isinstance(summary, str) or not summary.strip():

        assessment["quantitative_summary"] = (
            generate_fallback_summary(assessment)
        )

    # -------------------------------------------------
    # ADD RELEVANT LIMITATIONS
    # -------------------------------------------------

    if has_methodology and not has_direct:

        limitation = (
            "Methodology statistics describe research procedures "
            "and must not be interpreted as academic performance."
        )

        if limitation not in assessment["limitations"]:

            assessment["limitations"].append(limitation)

    if has_indirect and not has_direct:

        limitation = (
            "Indirect educational outcomes such as motivation "
            "and engagement do not independently demonstrate "
            "improved academic achievement."
        )

        if limitation not in assessment["limitations"]:

            assessment["limitations"].append(limitation)

    return assessment


def analyze_quantitative_evidence(
    client,
    model,
    evaluated_evidence
):
    """
    Extract and classify quantitative research evidence.

    Separates:
    1. Study characteristics.
    2. Methodology statistics.
    3. Direct academic outcomes.
    4. Indirect educational outcomes.
    """

    if not isinstance(evaluated_evidence, list):

        raise ValueError(
            "Evaluated evidence must be provided as a list."
        )

    quantitative_records = []

    total = len(evaluated_evidence)

    for number, record in enumerate(
        evaluated_evidence,
        start=1
    ):

        print(
            f"\nAnalyzing quantitative evidence "
            f"{number}/{total}..."
        )

        abstract = record.get("abstract")

        if not isinstance(abstract, str) or not abstract.strip():

            print("Skipped: Abstract unavailable.")
            continue

        title = record.get(
            "title",
            "Unknown publication"
        )

        year = record.get("year")

        doi = record.get("doi")

        publication_id = record.get("publication_id")

        abstract = abstract[:5000]

        # -------------------------------------------------
        # GEMINI EXTRACTION PROMPT
        # -------------------------------------------------

        prompt = f"""
You are the quantitative evidence extraction component
of VeriAgent, an AI research claim verification agent.

Analyze the following research abstract.

RESEARCH CLAIM:
Artificial intelligence improves student academic performance.

PUBLICATION:
Title: {title}
Year: {year}
DOI: {doi}

ABSTRACT:
{abstract}

YOUR TASK:

Extract numerical findings and classify them accurately.

CATEGORY 1: STUDY CHARACTERISTICS

Examples:
- 250 students participated.
- 20 studies were included.
- 700 articles were initially identified.

These describe the research, not its effectiveness.

IMPORTANT SAMPLE SIZE EXTRACTION:

Extract the total number of human participants or students
when explicitly reported in the abstract.

Return sample_size as an object:

{{
    "value": 200,
    "unit": "students"
}}

Examples:
- "200 students participated" -> 200 students
- "A sample of 120 respondents" -> 120 respondents
- "The study included 64 undergraduate students" -> 64 students
- "N = 150" -> 150 participants

If no participant sample size is explicitly reported,
return null.

Do not confuse:
- Number of participants
- Number of studies reviewed
- Number of articles identified
- Percentages
- Number of institutions

Record additional study characteristics in study_characteristics.

CATEGORY 2: METHODOLOGY STATISTICS

Examples:
- 29% of studies used machine learning.
- 60% of publications used surveys.
- 40% used qualitative research methods.

Record these in methodology_statistics.

These are NOT academic performance outcomes.

CATEGORY 3: DIRECT ACADEMIC OUTCOMES

Examples:
- Examination scores.
- Student grades.
- Mean test scores.
- Learning gains.
- Knowledge acquisition scores.
- Academic achievement effect sizes.

Record these in direct_outcome_evidence.

Preserve exact values, measures, context and direction.

CATEGORY 4: INDIRECT EDUCATIONAL OUTCOMES

Examples:
- Motivation.
- Engagement.
- Satisfaction.
- Attitudes.
- Anxiety.
- Self-efficacy.

Record these in indirect_outcome_evidence.

These are NOT direct academic achievement.

STATISTICAL MEASURES:

Extract when explicitly reported:

- Percentages.
- Effect sizes.
- P-values.
- Confidence intervals.
- Means and standard deviations.
- Mean differences.
- Other numerical outcome statistics.

Keep the statistical measure connected to the outcome
it actually measures.

IMPORTANT RULES:

1. Use only the supplied abstract.
2. Never invent or estimate values.
3. Preserve exact reported values and units.
4. Do not infer causation from correlation.
5. Do not interpret sample size as effectiveness.
6. Do not interpret methodology percentages as outcomes.
7. Do not treat engagement or satisfaction as achievement.
8. Preserve negative, null and mixed findings.
9. Separate participant counts from study counts.
10. Do not classify a p-value without identifying its outcome.
11. A statistically significant result does not automatically
    mean a practically important improvement.
12. Do not place the same statistic in multiple categories
    unless it genuinely measures multiple outcomes.
13. If an outcome's meaning is unclear, state this limitation.
14. Do not claim that AI caused improvement unless the
    abstract explicitly supports that conclusion.
15. Write a concise quantitative_summary of 1-3 sentences.
16. The summary must describe what was actually reported.
17. Do not leave the summary empty when information is available.
18. If the abstract has no numerical information, say so.

OUTCOME CLASSIFICATION:

Use exactly one:

- direct_outcome
- indirect_outcome
- methodology_only
- mixed
- no_outcome_statistics
- unknown

Use mixed only when BOTH direct and indirect outcomes
are actually reported.

Use direct_outcome when only direct outcomes are reported.

Use indirect_outcome when only indirect outcomes are reported.

Use methodology_only when only methodological statistics
are reported.

Use no_outcome_statistics when numerical information exists
but no outcome statistics are reported.

Use unknown when there is insufficient information.

RETURN ONLY VALID JSON:

{{
    "has_quantitative_data": false,
    "has_direct_outcome_statistics": false,
    "outcome_relevance": "unknown",
    "sample_size": null,
    "study_characteristics": [],
    "methodology_statistics": [],
    "outcome_statistics": [],
    "direct_outcome_evidence": [],
    "indirect_outcome_evidence": [],
    "percentages": [],
    "effect_sizes": [],
    "p_values": [],
    "confidence_intervals": [],
    "other_statistics": [],
    "quantitative_summary": "",
    "limitations": []
}}

For each finding, use objects with relevant fields such as:
"value", "measure", "description", "context".

Do not copy example values.
Return valid JSON only.
"""

        # -------------------------------------------------
        # REQUEST QUANTITATIVE EXTRACTION
        # -------------------------------------------------

        try:

            response = client.interactions.create(
                model=model,
                input=prompt
            )

            assessment = extract_json(
                response.output_text
            )

            assessment = normalize_assessment(
                assessment,
                abstract
            )

            quantitative_record = {
                "publication_id": publication_id,
                "title": title,
                "year": year,
                "doi": doi,
                "quantitative_assessment": assessment
            }

            quantitative_records.append(
                quantitative_record
            )

            # -------------------------------------------------
            # DISPLAY RESULTS
            # -------------------------------------------------

            relevance = assessment["outcome_relevance"]

            if relevance == "direct_outcome":

                print(
                    "Direct academic outcome statistics identified!"
                )

            elif relevance == "indirect_outcome":

                print(
                    "Indirect educational outcome statistics identified."
                )

            elif relevance == "mixed":

                print(
                    "Both direct and indirect outcome statistics identified."
                )

            elif relevance == "methodology_only":

                print(
                    "Methodology statistics identified, "
                    "but no direct academic outcomes."
                )

            elif assessment["has_quantitative_data"]:

                print(
                    "Numerical study information identified."
                )

            else:

                print(
                    "No quantitative information identified."
                )

            sample_size = assessment.get("sample_size")

            if sample_size:

                print(
                    "Sample size:",
                    sample_size["value"],
                    sample_size["unit"]
                )

            else:

                print("Sample size: Not reported")

        except Exception as error:

            print(
                f"Quantitative analysis error: {error}"
            )

            assessment = create_empty_assessment(
                error_message=(
                    f"AI extraction request failed: {str(error)}"
                )
            )

            quantitative_records.append({
                "publication_id": publication_id,
                "title": title,
                "year": year,
                "doi": doi,
                "quantitative_assessment": assessment
            })

    # -------------------------------------------------
    # OVERALL QUANTITATIVE SUMMARY
    # -------------------------------------------------

    total_analyzed = len(quantitative_records)

    with_quantitative_data = sum(
        1
        for record in quantitative_records
        if record["quantitative_assessment"][
            "has_quantitative_data"
        ]
    )

    with_direct_outcomes = sum(
        1
        for record in quantitative_records
        if record["quantitative_assessment"][
            "has_direct_outcome_statistics"
        ]
    )

    with_indirect_outcomes = sum(
        1
        for record in quantitative_records
        if record["quantitative_assessment"][
            "indirect_outcome_evidence"
        ]
    )

    with_methodology_statistics = sum(
        1
        for record in quantitative_records
        if record["quantitative_assessment"][
            "methodology_statistics"
        ]
    )

    print("\n" + "=" * 55)
    print("QUANTITATIVE ANALYSIS SUMMARY")
    print("=" * 55)

    print("Publications analyzed:", total_analyzed)

    print(
        "Publications with numerical information:",
        with_quantitative_data
    )

    print(
        "Publications with direct academic outcome statistics:",
        with_direct_outcomes
    )

    print(
        "Publications with indirect educational outcome statistics:",
        with_indirect_outcomes
    )

    print(
        "Publications with methodology statistics:",
        with_methodology_statistics
    )

    print(
        "Note: Direct and indirect counts may overlap "
        "for publications classified as mixed."
    )

    print("=" * 55)

    return quantitative_records
