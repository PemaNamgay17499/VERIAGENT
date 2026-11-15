
import streamlit as st
import pandas as pd
import html
import json
from datetime import datetime

from agent import VeriAgent
from memory.memory import get_claim_history, save_feedback


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="VeriAgent | AI Research Verification",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# BLUE CARD COLOR THEME
# ============================================================

st.markdown("""
<style>

/* ---------------- GLOBAL ---------------- */

:root {
    --cyan: #00FFFF;
    --sky: #00CCFF;
    --cerulean: #0099FF;
    --dodger: #0066FF;
    --blue: #0033FF;
    --white: #FFFFFF;

    --background: #071426;
    --surface: #0D203A;
    --surface-light: #122B4A;
    --border: rgba(0, 153, 255, 0.22);
    --muted: #A9BCD2;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--background);
    color: var(--white);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stMain"] {
    background: var(--background);
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

/* ---------------- SIDEBAR ---------------- */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #081A32 0%,
        #0B2443 55%,
        #071426 100%
    );
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: var(--white);
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 9px 12px;
    border-radius: 9px;
    transition: 0.2s ease;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(0, 153, 255, 0.15);
}

/* ---------------- TYPOGRAPHY ---------------- */

h1, h2, h3, h4 {
    color: var(--white) !important;
    letter-spacing: -0.5px;
}

p, label, li {
    color: #DCE9F7;
}

.small-muted {
    color: var(--muted);
    font-size: 0.88rem;
}

/* ---------------- HERO ---------------- */

.hero {
    padding: 30px;
    border-radius: 18px;
    background: linear-gradient(
        115deg,
        #0D203A 0%,
        #103C70 50%,
        #0033FF 130%
    );
    border: 1px solid rgba(0, 204, 255, 0.35);
    margin-bottom: 24px;
    box-shadow: 0 10px 35px rgba(0, 51, 255, 0.12);
}

.hero-label {
    color: var(--cyan);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.hero h1 {
    font-size: 2.25rem;
    margin: 10px 0 8px 0;
    font-weight: 800;
}

.hero p {
    color: #D7E9FF;
    font-size: 1rem;
    max-width: 760px;
    margin-bottom: 0;
}

/* ---------------- CARDS ---------------- */

.metric-card {
    background: linear-gradient(
        145deg,
        #102A49,
        #0B1D35
    );
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px;
    min-height: 115px;
}

.metric-label {
    color: #AFC7E2;
    font-size: 0.82rem;
    margin-bottom: 10px;
}

.metric-value {
    color: var(--white);
    font-size: 1.8rem;
    font-weight: 800;
}

.metric-caption {
    color: var(--sky);
    font-size: 0.78rem;
    margin-top: 5px;
}

.content-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
}

.evidence-card {
    background: #0D203A;
    border: 1px solid rgba(0, 153, 255, 0.20);
    border-left: 4px solid var(--cerulean);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
}

.section-heading {
    font-size: 1.15rem;
    font-weight: 750;
    margin-bottom: 12px;
    color: var(--white);
}

/* ---------------- VERDICT ---------------- */

.verdict-supported {
    border-left: 5px solid #00CCFF;
}

.verdict-refuted {
    border-left: 5px solid #FF647C;
}

.verdict-inconclusive {
    border-left: 5px solid #D9B45B;
}

.verdict-unverified {
    border-left: 5px solid #A9BCD2;
}

.verdict-title {
    font-size: 1.55rem;
    font-weight: 800;
    color: var(--white);
}

.verdict-description {
    color: #C5D8EC;
    margin-top: 8px;
}

/* ---------------- BUTTONS ---------------- */

.stButton > button {
    background: linear-gradient(
        110deg,
        #0099FF,
        #0066FF,
        #0033FF
    );
    color: white !important;
    border: 1px solid rgba(0, 255, 255, 0.35);
    border-radius: 9px;
    padding: 0.55rem 1.1rem;
    font-weight: 700;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: linear-gradient(
        110deg,
        #00CCFF,
        #0099FF
    );
    border-color: var(--cyan);
    box-shadow: 0 0 16px rgba(0, 204, 255, 0.22);
    transform: translateY(-1px);
}

/* ---------------- INPUTS ---------------- */

.stTextArea textarea,
.stTextInput input {
    background: #0B1D35 !important;
    color: white !important;
    border: 1px solid rgba(0, 153, 255, 0.35) !important;
    border-radius: 9px !important;
}

.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 1px var(--cyan) !important;
}

[data-baseweb="select"] > div {
    background: #0B1D35 !important;
    border-color: rgba(0, 153, 255, 0.35) !important;
    color: white !important;
}

/* ---------------- TABS ---------------- */

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    color: #B8CEE5;
    background: transparent;
    border-radius: 8px 8px 0 0;
    padding: 10px 15px;
}

.stTabs [aria-selected="true"] {
    color: var(--cyan) !important;
    border-bottom: 2px solid var(--cyan) !important;
}

/* ---------------- ALERTS ---------------- */

[data-testid="stAlert"] {
    background: #102A49;
    border: 1px solid var(--border);
    border-radius: 10px;
}

/* ---------------- DATAFRAMES ---------------- */

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 10px;
}

/* ---------------- DIVIDER / FOOTER ---------------- */

hr {
    border-color: rgba(0, 153, 255, 0.20);
}

.footer {
    text-align: center;
    color: #809BB8;
    font-size: 0.8rem;
    padding: 22px 0 5px 0;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD AGENT
# ============================================================

@st.cache_resource
def load_agent():
    return VeriAgent()


try:
    agent = load_agent()
except Exception as error:
    st.error(f"Could not initialize VeriAgent: {error}")
    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "result" not in st.session_state:
    st.session_state.result = None

if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

if "research_running" not in st.session_state:
    st.session_state.research_running = False

if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_text(value, default="Not available"):
    """Convert values into safe readable text."""

    if value is None:
        return default

    if isinstance(value, (dict, list)):
        return str(value)

    return str(value)


def get_value(data, *keys, default=None):
    """Get the first available key from a dictionary."""

    if not isinstance(data, dict):
        return default

    for key in keys:
        value = data.get(key)

        if value is not None:
            return value

    return default


def normalize_list(value):
    """Ensure a value is represented as a list."""

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    return [value]


def get_decision(result):
    """Retrieve the most recent decision."""

    if not isinstance(result, dict):
        return {}

    decision = result.get("decision")

    if isinstance(decision, dict):
        return decision

    adaptive = result.get("adaptive_decision")

    if isinstance(adaptive, dict):
        return adaptive

    initial = result.get("initial_decision")

    if isinstance(initial, dict):
        return initial

    return {}


def get_verdict(result):
    """Extract the final verdict."""

    decision = get_decision(result)

    verdict = get_value(
        decision,
        "verdict",
        "decision",
        "conclusion",
        "status",
        default=None
    )

    if verdict:
        return safe_text(verdict)

    return safe_text(
        get_value(
            result,
            "verdict",
            "conclusion",
            default="Inconclusive"
        )
    )


def get_confidence(result):
    decision = get_decision(result)

    return safe_text(
        get_value(
            decision,
            "confidence",
            "confidence_level",
            default="Not available"
        )
    )


def get_explanation(result):
    decision = get_decision(result)

    return safe_text(
        get_value(
            decision,
            "explanation",
            "reasoning",
            "justification",
            "summary",
            default="No explanation was provided."
        )
    )


def get_evidence(result):
    """Get the latest combined evidence when available."""

    if not isinstance(result, dict):
        return []

    combined = result.get("combined_evidence")

    if isinstance(combined, list):
        return combined

    eligible = result.get("eligible_evidence")

    if isinstance(eligible, list):
        return eligible

    evaluated = result.get("evaluated_evidence")

    return normalize_list(evaluated)


def get_publications(result):
    if not isinstance(result, dict):
        return []

    return normalize_list(result.get("publications"))


def get_eligible_count(result):
    evidence = get_evidence(result)

    count = 0

    for item in evidence:
        if not isinstance(item, dict):
            continue

        quality = item.get("quality_assessment", {})

        if isinstance(quality, dict):
            if quality.get("eligible_for_decision") is True:
                count += 1

    if count == 0:
        eligible = result.get("eligible_evidence", [])

        if isinstance(eligible, list):
            count = len(eligible)

    return count


def get_verdict_style(verdict):
    value = verdict.lower()

    if "support" in value:
        return "verdict-supported"

    if "refut" in value or "reject" in value:
        return "verdict-refuted"

    if "inconclusive" in value or "uncertain" in value:
        return "verdict-inconclusive"

    return "verdict-unverified"


def render_metric(label, value, caption=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(str(label))}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
            <div class="metric-caption">{html.escape(str(caption))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_verdict(result):
    verdict = get_verdict(result)
    confidence = get_confidence(result)
    explanation = get_explanation(result)

    style = get_verdict_style(verdict)

    st.markdown(
        f"""
        <div class="content-card {style}">
            <div class="small-muted">FINAL VERIFICATION RESULT</div>
            <div class="verdict-title">
                {html.escape(verdict)}
            </div>
            <div style="color:#00CCFF;font-weight:700;margin-top:5px;">
                Confidence: {html.escape(confidence)}
            </div>
            <div class="verdict-description">
                {html.escape(explanation)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_publication(publication, index):
    if not isinstance(publication, dict):
        return

    title = get_value(
        publication,
        "title",
        "display_name",
        default=f"Publication {index + 1}"
    )

    year = get_value(publication, "year", default="Year unavailable")
    doi = get_value(publication, "doi", default="Not available")

    authors = get_value(
        publication,
        "authors",
        "author",
        default="Not available"
    )

    st.markdown(
        f"""
        <div class="evidence-card">
            <div style="font-weight:750;color:#FFFFFF;">
                {html.escape(safe_text(title))}
            </div>
            <div class="small-muted" style="margin-top:8px;">
                Year: {html.escape(safe_text(year))}
                &nbsp; | &nbsp;
                DOI: {html.escape(safe_text(doi))}
            </div>
            <div class="small-muted" style="margin-top:5px;">
                Authors: {html.escape(safe_text(authors))}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_evidence(evidence, index):
    if not isinstance(evidence, dict):
        return

    title = get_value(
        evidence,
        "title",
        default=f"Evidence {index + 1}"
    )

    year = get_value(evidence, "year", default="Unknown")
    classification = get_value(
        evidence,
        "classification",
        default="Not classified"
    )

    relevance = get_value(
        evidence,
        "relevance",
        default="Not available"
    )

    study_type = get_value(
        evidence,
        "study_type",
        default="Not available"
    )

    findings = get_value(
        evidence,
        "findings_status",
        default="Not available"
    )

    strength = get_value(
        evidence,
        "evidence_strength",
        default="Not available"
    )

    explanation = get_value(
        evidence,
        "explanation",
        default="No explanation available."
    )

    quality = evidence.get("quality_assessment", {})

    eligible = "Not assessed"

    if isinstance(quality, dict):
        eligible = (
            "Eligible for decision"
            if quality.get("eligible_for_decision") is True
            else "Not eligible for decision"
        )

    with st.expander(f"{index + 1}. {safe_text(title)}"):
        st.write(f"**Year:** {safe_text(year)}")
        st.write(f"**Classification:** {safe_text(classification)}")
        st.write(f"**Relevance:** {safe_text(relevance)}")
        st.write(f"**Study type:** {safe_text(study_type)}")
        st.write(f"**Findings:** {safe_text(findings)}")
        st.write(f"**Evidence strength:** {safe_text(strength)}")
        st.write(f"**Research quality:** {eligible}")
        st.write(f"**Explanation:** {safe_text(explanation)}")


def render_quantitative_evidence(result):
    quantitative = result.get("quantitative_evidence", {})

    if not isinstance(quantitative, dict) or not quantitative:
        st.info("No quantitative analysis is available yet.")
        return

    summary = get_value(
        quantitative,
        "quantitative_summary",
        "summary",
        default="No quantitative summary available."
    )

    st.markdown("### Quantitative analysis")
    st.write(summary)

    fields = [
        ("Outcome relevance", "outcome_relevance"),
        ("Sample size", "sample_size"),
        ("Percentages", "percentages"),
        ("Effect sizes", "effect_sizes"),
        ("P-values", "p_values"),
        ("Confidence intervals", "confidence_intervals"),
        ("Other statistics", "other_statistics")
    ]

    for label, key in fields:
        value = quantitative.get(key)

        if value is not None:
            st.markdown(f"**{label}:**")
            st.write(value)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center;padding:18px 5px 25px 5px;">
            <div style="font-size:2.7rem;">🔷</div>
            <div style="
                font-size:1.55rem;
                font-weight:850;
                color:#FFFFFF;
                letter-spacing:1px;
            ">
                VeriAgent
            </div>
            <div style="
                color:#00CCFF;
                font-size:0.72rem;
                letter-spacing:2px;
                margin-top:5px;
            ">
                RESEARCH INTELLIGENCE
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "Research History",
            "About VeriAgent"
        ],
        label_visibility="visible"
    )

    st.session_state.active_page = page

    st.markdown("---")

    st.markdown(
        """
        <div style="
            background:rgba(0,153,255,0.10);
            border:1px solid rgba(0,153,255,0.25);
            padding:14px;
            border-radius:10px;
        ">
            <div style="color:#00FFFF;font-weight:700;">
                AI Research Agent
            </div>
            <div style="font-size:0.82rem;color:#B8CEE5;margin-top:7px;">
                An intelligent system for claim verification,
                evidence evaluation and adaptive research.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DASHBOARD PAGE
# ============================================================

if page == "Dashboard":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-label">AI-POWERED RESEARCH VERIFICATION</div>
            <h1>Verify claims with intelligent research.</h1>
            <p>
                VeriAgent investigates research claims, retrieves academic
                publications, evaluates evidence quality and adapts its
                research strategy to improve its conclusions.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------- CLAIM INPUT ----------------

    st.markdown("### Start a new verification")

    claim = st.text_area(
        "Enter a research claim",
        placeholder=(
            "Example: Artificial intelligence improves "
            "student academic performance."
        ),
        height=105,
        key="claim_input"
    )

    col1, col2 = st.columns([1, 5])

    with col1:
        verify_button = st.button(
            "🔍 Verify Claim",
            use_container_width=True
        )

    with col2:
        if st.session_state.result:
            st.caption("Your latest verification result is available below.")

    if verify_button:

        if not claim.strip():
            st.warning("Please enter a research claim before proceeding.")

        else:
            st.session_state.result = None
            st.session_state.feedback_submitted = False

            with st.spinner(
                "VeriAgent is investigating your claim and retrieving research evidence..."
            ):
                try:
                    result = agent.verify_claim(claim.strip())

                    if isinstance(result, dict):
                        st.session_state.result = result
                    else:
                        st.error(
                            "The verification process did not return "
                            "the expected result."
                        )

                except Exception as error:
                    st.error(f"Verification failed: {error}")

    # ---------------- RESULTS ----------------

    result = st.session_state.result

    if result:

        st.markdown("---")
        st.markdown("## Verification results")

        verified_claim = get_value(
            result,
            "claim",
            default="Claim unavailable"
        )

        st.markdown(
            f"""
            <div class="content-card">
                <div class="small-muted">CLAIM UNDER INVESTIGATION</div>
                <div style="
                    font-size:1.1rem;
                    font-weight:700;
                    color:#FFFFFF;
                    margin-top:8px;
                ">
                    {html.escape(safe_text(verified_claim))}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        publications = get_publications(result)
        evidence = get_evidence(result)

        total_publications = get_value(
            result,
            "total_publications",
            default=len(publications)
        )

        total_abstracts = get_value(
            result,
            "total_abstracts",
            default=0
        )

        evaluated_count = len(
            normalize_list(result.get("evaluated_evidence"))
        )

        eligible_count = get_eligible_count(result)

        metric1, metric2, metric3, metric4 = st.columns(4)

        with metric1:
            render_metric(
                "Publications",
                total_publications,
                "Research records retrieved"
            )

        with metric2:
            render_metric(
                "Abstracts",
                total_abstracts,
                "Abstracts retrieved"
            )

        with metric3:
            render_metric(
                "Evaluated evidence",
                evaluated_count,
                "Evidence records assessed initially"
            )

        with metric4:
            render_metric(
                "Eligible evidence",
                eligible_count,
                "Evidence meeting quality criteria"
            )

        st.markdown("### Final decision")
        render_verdict(result)

        # ---------------- RESULT TABS ----------------

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Analytics",
            "📚 Evidence Explorer",
            "🧠 Agent Reasoning",
            "🔄 Adaptive Research",
            "📈 Quantitative Analysis"
        ])

        # ---------------- ANALYTICS ----------------

        with tab1:

            st.markdown("### Research overview")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    '<div class="content-card">',
                    unsafe_allow_html=True
                )

                st.markdown("**Verification summary**")
                st.write(f"**Verdict:** {get_verdict(result)}")
                st.write(f"**Confidence:** {get_confidence(result)}")
                st.write(f"**Publications:** {total_publications}")
                st.write(f"**Evaluated evidence:** {evaluated_count}")
                st.write(f"**Eligible evidence:** {eligible_count}")

                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown(
                    '<div class="content-card">',
                    unsafe_allow_html=True
                )

                st.markdown("**Research activity**")

                additional_publications = result.get(
                    "additional_publications", []
                )

                additional_evaluations = result.get(
                    "additional_evaluations", []
                )

                queries = result.get("adaptive_queries", [])

                st.write(
                    f"**Additional publications:** "
                    f"{len(normalize_list(additional_publications))}"
                )

                st.write(
                    f"**Additional evaluations:** "
                    f"{len(normalize_list(additional_evaluations))}"
                )

                st.write(
                    f"**Adaptive search queries:** "
                    f"{len(normalize_list(queries))}"
                )

                st.markdown("</div>", unsafe_allow_html=True)

            # Evidence classification chart

            classifications = {}

            for item in evidence:

                if not isinstance(item, dict):
                    continue

                category = safe_text(
                    item.get("classification"),
                    "Unclassified"
                )

                classifications[category] = (
                    classifications.get(category, 0) + 1
                )

            if classifications:

                st.markdown("### Evidence classification")

                chart_data = pd.DataFrame(
                    list(classifications.items()),
                    columns=["Classification", "Count"]
                ).set_index("Classification")

                st.bar_chart(
                    chart_data,
                    color="#0099FF"
                )

        # ---------------- EVIDENCE EXPLORER ----------------

        with tab2:

            st.markdown("### Retrieved publications")

            if publications:

                for index, publication in enumerate(publications):
                    render_publication(publication, index)

            else:
                st.info("No publication records are available.")

            st.markdown("---")
            st.markdown("### Evaluated evidence")

            if evidence:

                for index, item in enumerate(evidence):
                    render_evidence(item, index)

            else:
                st.info("No evaluated evidence is available.")

        # ---------------- AGENT REASONING ----------------

        with tab3:

            st.markdown("### Claim analysis")

            analysis = result.get("analysis")

            if isinstance(analysis, dict):
                st.json(analysis)
            elif analysis:
                st.write(analysis)
            else:
                st.info("No claim analysis is available.")

            st.markdown("---")
            st.markdown("### Decision explanation")

            st.write(get_explanation(result))

            st.markdown("---")
            st.markdown("### Initial decision")

            initial_decision = result.get("initial_decision")

            if initial_decision:
                st.json(initial_decision)
            else:
                st.info("Initial decision details are unavailable.")

            if result.get("adaptive_decision"):
                st.markdown("### Adaptive decision")
                st.json(result["adaptive_decision"])

            if result.get("reflection"):
                st.markdown("### Agent reflection")
                st.write(result["reflection"])

        # ---------------- ADAPTIVE RESEARCH ----------------

        with tab4:

            st.markdown("### Improve the research through feedback")

            st.write(
                "Provide feedback on the current verification result. "
                "VeriAgent can reflect on your feedback, generate "
                "additional research queries and update its conclusion."
            )

            if result.get("adaptive_claim_id"):

                st.success(
                    "Adaptive research has already been completed "
                    "for this verification."
                )

            else:

                feedback = st.text_area(
                    "Your feedback",
                    placeholder=(
                        "Example: The evidence should include more "
                        "recent studies and research with larger "
                        "sample sizes."
                    ),
                    height=110,
                    key="user_feedback"
                )

                if st.button(
                    "🔄 Submit Feedback & Improve Research",
                    use_container_width=True
                ):

                    claim_id = result.get("claim_id")

                    if not claim_id:
                        st.error(
                            "A claim ID is missing. Feedback cannot be saved."
                        )

                    elif not feedback.strip():
                        st.warning("Please provide feedback first.")

                    else:

                        try:

                            with st.spinner(
                                "VeriAgent is reflecting on your feedback "
                                "and conducting adaptive research..."
                            ):

                                # Save feedback to the memory system.
                                save_feedback(
                                    claim_id,
                                    feedback.strip()
                                )

                                result["user_feedback"] = feedback.strip()

                                # Reflection stage.
                                reflection = agent.reflect(result)

                                if reflection is not None:
                                    result["reflection"] = reflection

                                # Adaptive research stage.
                                adaptive_result = agent.adapt_research(result)

                                if isinstance(adaptive_result, dict):
                                    result.update(adaptive_result)

                                st.session_state.result = result
                                st.session_state.feedback_submitted = True

                            st.success(
                                "Adaptive research completed successfully."
                            )

                            st.rerun()

                        except Exception as error:
                            st.error(
                                f"Adaptive research failed: {error}"
                            )

            # Display adaptive research details.

            st.markdown("---")
            st.markdown("### Adaptive research activity")

            adaptive_queries = normalize_list(
                result.get("adaptive_queries")
            )

            if adaptive_queries:

                st.markdown("**Generated research queries**")

                for index, query in enumerate(adaptive_queries):
                    st.markdown(
                        f"- {html.escape(safe_text(query))}"
                    )

            else:
                st.info(
                    "Adaptive research queries will appear here "
                    "after feedback is submitted."
                )

            additional_publications = normalize_list(
                result.get("additional_publications")
            )

            st.markdown(
                f"**Additional publications retrieved:** "
                f"{len(additional_publications)}"
            )

            additional_evaluations = normalize_list(
                result.get("additional_evaluations")
            )

            st.markdown(
                f"**Additional evidence evaluations:** "
                f"{len(additional_evaluations)}"
            )

            if result.get("reflection"):
                st.markdown("**Agent reflection**")
                st.write(result["reflection"])

        # ---------------- QUANTITATIVE ANALYSIS ----------------

        with tab5:

            render_quantitative_evidence(result)

    else:

        # ---------------- EMPTY DASHBOARD ----------------

        st.markdown("---")

        st.markdown(
            """
            <div class="content-card" style="text-align:center;padding:45px 20px;">
                <div style="font-size:3rem;">🔬</div>
                <h3 style="margin-top:15px;">Ready to investigate?</h3>
                <p style="color:#AFC7E2;">
                    Enter a research claim above to begin the
                    intelligent verification process.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# RESEARCH HISTORY PAGE
# ============================================================

elif page == "Research History":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-label">RESEARCH MEMORY</div>
            <h1>Research History</h1>
            <p>
                Review previously investigated claims and
                access your stored verification records.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    try:

        history = get_claim_history(limit=50)

        if isinstance(history, pd.DataFrame):

            if not history.empty:

                st.markdown("### Previous verification records")

                st.dataframe(
                    history,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No research history is available yet.")

        elif isinstance(history, list):

            if history:

                history_df = pd.DataFrame(history)

                st.markdown("### Previous verification records")

                st.dataframe(
                    history_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No research history is available yet.")

        elif isinstance(history, dict):

            st.markdown("### Previous verification records")
            st.json(history)

        elif history is None:

            st.info("No research history is available yet.")

        else:

            st.write(history)

    except Exception as error:

        st.error(f"Could not load research history: {error}")


# ============================================================
# ABOUT PAGE
# ============================================================

elif page == "About VeriAgent":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-label">ABOUT THE SYSTEM</div>
            <h1>Understanding VeriAgent</h1>
            <p>
                An adaptive AI research agent designed to investigate
                claims through academic evidence retrieval,
                evaluation and iterative reasoning.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## What is VeriAgent?")

    st.markdown(
        """
        <div class="content-card">
            VeriAgent is an AI-powered research claim verification system.
            It investigates user-submitted claims by retrieving academic
            publications, evaluating the relevance and quality of evidence,
            and generating an evidence-based conclusion.

            <br><br>

            Unlike a basic question-answering system, VeriAgent can use
            user feedback to reflect on its initial research, generate
            additional search queries and conduct further research.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## How the agent works")

    stages = [
        (
            "01",
            "Claim Analysis",
            "Examines the submitted claim and identifies its key concepts."
        ),
        (
            "02",
            "Research Planning",
            "Develops search queries to retrieve relevant academic publications."
        ),
        (
            "03",
            "Evidence Retrieval",
            "Searches academic sources and collects relevant research records."
        ),
        (
            "04",
            "Evidence Evaluation",
            "Assesses the relevance, findings and quality of retrieved evidence."
        ),
        (
            "05",
            "Decision Making",
            "Combines evaluated evidence to determine an initial conclusion."
        ),
        (
            "06",
            "Reflection and Adaptation",
            "Uses feedback to reconsider the research and generate additional queries."
        ),
        (
            "07",
            "Final Verification",
            "Combines additional evidence and updates the final decision."
        )
    ]

    for number, title, description in stages:

        st.markdown(
            f"""
            <div class="evidence-card">
                <div style="display:flex;gap:15px;align-items:flex-start;">
                    <div style="
                        color:#00FFFF;
                        font-size:1.3rem;
                        font-weight:850;
                        min-width:35px;
                    ">
                        {number}
                    </div>
                    <div>
                        <div style="
                            color:#FFFFFF;
                            font-weight:750;
                            font-size:1rem;
                        ">
                            {title}
                        </div>
                        <div style="
                            color:#AFC7E2;
                            margin-top:5px;
                            font-size:0.9rem;
                        ">
                            {description}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("## Core capabilities")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            <div class="content-card">
                <h4>🔎 Academic Research</h4>
                <p class="small-muted">
                    Retrieves publications and research evidence
                    relevant to submitted claims.
                </p>
            </div>

            <div class="content-card">
                <h4>🧠 Intelligent Reasoning</h4>
                <p class="small-muted">
                    Evaluates evidence and generates
                    research-based decisions.
                </p>
            </div>

            <div class="content-card">
                <h4>📊 Quantitative Analysis</h4>
                <p class="small-muted">
                    Identifies available statistical information
                    from retrieved research.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            """
            <div class="content-card">
                <h4>🔄 Adaptive Research</h4>
                <p class="small-muted">
                    Uses feedback to improve its research strategy
                    and retrieve additional evidence.
                </p>
            </div>

            <div class="content-card">
                <h4>💾 Research Memory</h4>
                <p class="small-muted">
                    Stores claim verification records and
                    feedback for future reference.
                </p>
            </div>

            <div class="content-card">
                <h4>⚖️ Evidence-Based Decisions</h4>
                <p class="small-muted">
                    Produces conclusions based on the available
                    research evidence.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("## Important limitation")

    st.info(
        "VeriAgent supports research investigation and evidence assessment. "
        "Its conclusions depend on the availability, quality and coverage "
        "of retrieved publications. Results should be interpreted critically "
        "and are not a substitute for expert academic review."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        <div style="color:#00CCFF;font-weight:750;letter-spacing:1px;">
            VERIAGENT
        </div>
        AI-Powered Research Claim Verification System
        <br>
        Built with Python, Streamlit and Gemini
    </div>
    """,
    unsafe_allow_html=True
)
