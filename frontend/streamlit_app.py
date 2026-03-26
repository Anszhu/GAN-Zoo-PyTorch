from __future__ import annotations

import html
import os
from typing import Dict

import requests
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from backend.app import analyze_payload
from backend.models.schemas import AnalysisRequest
from backend.services.analytics_service import load_dashboard_snapshot


def get_api_url() -> str:
    env_url = os.getenv("API_URL")
    if env_url:
        return env_url

    try:
        return st.secrets.get("API_URL", "http://127.0.0.1:8000")
    except StreamlitSecretNotFoundError:
        return "http://127.0.0.1:8000"


API_URL = get_api_url()
USE_REMOTE_API = bool(os.getenv("API_URL"))


CUSTOM_CSS = """
<style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(255, 196, 0, 0.18), transparent 30%),
            radial-gradient(circle at top right, rgba(227, 66, 52, 0.12), transparent 25%),
            linear-gradient(180deg, #f8f4ea 0%, #fffaf3 55%, #f3eee5 100%);
        color: #231815;
    }
    .hero {
        padding: 1.6rem 1.8rem;
        border-radius: 24px;
        background: rgba(255,255,255,0.72);
        border: 1px solid rgba(35,24,21,0.08);
        box-shadow: 0 18px 60px rgba(70, 45, 34, 0.08);
    }
    .metric-card {
        padding: 1rem;
        border-radius: 18px;
        background: rgba(255,255,255,0.8);
        border: 1px solid rgba(35,24,21,0.08);
    }
    .highlight {
        background: #ffd7d1;
        border-bottom: 2px solid #b42318;
        padding: 0 3px;
        border-radius: 4px;
    }
</style>
"""

def annotate_text(text: str, highlights: list[Dict[str, object]]) -> str:
    if not highlights:
        return html.escape(text)

    ordered = sorted(highlights, key=lambda item: int(item["start"]))
    result = []
    cursor = 0
    for item in ordered:
        start = int(item["start"])
        end = int(item["end"])
        result.append(html.escape(text[cursor:start]))
        snippet = html.escape(text[start:end])
        result.append(f"<span class='highlight' title='{item['label']}'>{snippet}</span>")
        cursor = end
    result.append(html.escape(text[cursor:]))
    return "".join(result)


def analyze_text(text: str) -> Dict[str, object] | None:
    if USE_REMOTE_API:
        try:
            response = requests.post(
                f"{API_URL}/analyze",
                json={"text": text, "source": "streamlit-ui", "consent": True},
                timeout=15,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            st.error(f"API connection failed: {exc}")
            return None

    result = analyze_payload(
        AnalysisRequest(text=text, source="streamlit-standalone", consent=True)
    )
    return result.model_dump(mode="json")


def fetch_dashboard() -> Dict[str, object]:
    if USE_REMOTE_API:
        try:
            response = requests.get(f"{API_URL}/dashboard", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {"total_requests": 0, "severity_counts": {}, "language_counts": {}, "avg_score": 0.0}

    return load_dashboard_snapshot().model_dump(mode="json")


def main() -> None:
    st.set_page_config(
        page_title="DetectNet",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    st.sidebar.title("DetectNet")
    page = st.sidebar.radio("Navigate", ["Live Analysis", "Dashboard", "Project Notes"])
    st.sidebar.caption("Hybrid cyberbullying detection for English and Hindi")
    if USE_REMOTE_API:
        st.sidebar.markdown(f"[FastAPI docs]({API_URL}/docs)")
    else:
        st.sidebar.caption("Standalone deployment mode enabled")

    if page == "Live Analysis":
        st.markdown(
            """
            <div class="hero">
                <h1>DetectNet</h1>
                <p>A hybrid rule-based and BERT-powered multilingual cyberbullying detection prototype.</p>
                <p>Use this for a final year demo: enter English or Hindi text, inspect the rule evidence, and explain the weighted fusion score.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        sample_text = st.selectbox(
            "Quick demo sample",
            [
                "",
                "You are such an idiot, nobody likes you.",
                "Tu bewakoof hai, sab tumse nafrat karte hain.",
                "Please stay calm, I want to help you report this abuse.",
            ],
        )

        user_text = st.text_area(
            "Enter a message for analysis",
            value=sample_text,
            height=180,
            placeholder="Type social media text, chat content, or a comment here...",
        )

        if st.button("Analyze Message", type="primary", use_container_width=True):
            if not user_text.strip():
                st.warning("Please enter some text first.")
            else:
                result = analyze_text(user_text)
                if result:
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Language", result["language"])
                    col2.metric("Rule Score", f'{result["rule_engine"]["score"]:.2f}')
                    col3.metric("ML Confidence", f'{result["ml_engine"]["confidence"]:.2f}')
                    col4.metric("Severity", result["fused"]["severity"].upper())

                    st.subheader("Highlighted Evidence")
                    st.markdown(
                        f"<div class='metric-card'>{annotate_text(user_text, result['rule_engine']['highlights'])}</div>",
                        unsafe_allow_html=True,
                    )

                    left, right = st.columns([1.3, 1])
                    with left:
                        st.subheader("Explainability Panel")
                        st.write(result["fused"]["math_note"])
                        st.write(f"Risk band: {result['fused']['risk_band']}")
                        st.write("ML reasoning:")
                        for note in result["ml_engine"]["explanation"]:
                            st.write(f"- {note}")

                        st.write("Recommendations:")
                        for note in result["recommendations"]:
                            st.write(f"- {note}")

                    with right:
                        st.subheader("Rule Matches")
                        if result["rule_engine"]["matches"]:
                            st.dataframe(result["rule_engine"]["matches"], use_container_width=True, hide_index=True)
                        else:
                            st.info("No rule triggers detected.")

                    with st.expander("Evidence Log Summary", expanded=True):
                        st.write(f"Timestamp: {result['evidence']['timestamp']}")
                        st.write(f"SHA-256 hash: `{result['evidence']['request_hash']}`")
                        st.write(result["disclaimer"])

    elif page == "Dashboard":
        snapshot = fetch_dashboard()

        st.title("Moderation Dashboard")
        top1, top2, top3 = st.columns(3)
        top1.metric("Total Requests", snapshot["total_requests"])
        top2.metric("Average Score", snapshot["avg_score"])
        top3.metric("Tracked Languages", len(snapshot["language_counts"]))

        sev_counts = snapshot["severity_counts"] or {"no-data": 0}
        lang_counts = snapshot["language_counts"] or {"no-data": 0}

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Severity Distribution")
            st.bar_chart(sev_counts)
        with col2:
            st.subheader("Language Share")
            st.bar_chart(lang_counts)

        st.info("Dashboard metrics are built from hashed evidence logs stored locally for demo purposes.")

    else:
        st.title("Project Notes")
        st.markdown(
            """
### Implemented in this build
- Hybrid detection using a rule engine plus a transformer-ready ML scoring module
- Automatic English/Hindi language detection without translation
- FastAPI endpoints for analysis, dashboard data, and mock reporting
- Streamlit multi-page interface with explainability and charts
- Evidence logging with timestamps and SHA-256 integrity hash

### Viva-friendly explanation
1. The rule engine catches explicit abusive patterns quickly and transparently.
2. The ML layer estimates contextual harm probability and reduces false positives.
3. A weighted fusion formula combines both scores into one final severity value.
4. High-risk outputs can be escalated through a mock reporting API for future government or NGO integration.

### Future scope
- Replace the current offline ML module with a fine-tuned BERT or XLM-RoBERTa model
- Add more Indian languages such as Tamil, Telugu, and Bengali
- Integrate authentication, role-based access, and secure cloud evidence storage
            """
        )
