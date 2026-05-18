"""Low-fidelity wireframe styling (grayscale, bordered cards) for Streamlit."""

import streamlit as st


def inject_wireframe_css() -> None:
    st.markdown(
        """
<style>
  :root {
    --wf-bg: #e8e8e8;
    --wf-panel: #ffffff;
    --wf-border: #bdbdbd;
    --wf-text: #212121;
    --wf-muted: #616161;
    --wf-accent: #424242;
  }
  .stApp {
    background-color: var(--wf-bg) !important;
    color: var(--wf-text);
  }
  [data-testid="stHeader"] {
    background-color: #dcdcdc !important;
    border-bottom: 1px solid var(--wf-border);
  }
  [data-testid="stSidebar"] {
    background-color: #f0f0f0 !important;
    border-right: 1px solid var(--wf-border) !important;
  }
  [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
  [data-testid="stSidebar"] label {
    color: var(--wf-text) !important;
  }
  div[data-testid="stVerticalBlock"] > div:has(> div.wf-card) {
    background: transparent;
  }
  .wf-card {
    background: var(--wf-panel);
    border: 1px solid var(--wf-border);
    border-radius: 4px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
    box-shadow: none;
  }
  .wf-card h1, .wf-card h2, .wf-card h3 {
    color: var(--wf-text) !important;
    font-weight: 600;
  }
  .wf-kpi {
    background: var(--wf-panel);
    border: 1px solid var(--wf-border);
    border-radius: 4px;
    padding: 0.75rem 1rem;
    text-align: center;
  }
  .wf-kpi .num { font-size: 1.5rem; font-weight: 700; color: var(--wf-accent); }
  .wf-kpi .lbl { font-size: 0.75rem; color: var(--wf-muted); text-transform: uppercase; letter-spacing: 0.04em; }
  div[data-testid="stMetric"] {
    background: var(--wf-panel);
    border: 1px solid var(--wf-border);
    border-radius: 4px;
    padding: 0.5rem 0.75rem;
  }
  div[data-testid="stMetric"] label {
    color: var(--wf-muted) !important;
  }
  div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--wf-accent) !important;
  }
  .stButton > button {
    background-color: #eeeeee !important;
    color: var(--wf-text) !important;
    border: 1px solid var(--wf-border) !important;
    border-radius: 4px !important;
  }
  .stButton > button:hover {
    background-color: #e0e0e0 !important;
    border-color: #9e9e9e !important;
  }
  [data-testid="stPrimaryButton"] > button {
    background-color: #757575 !important;
    color: #fff !important;
    border-color: #616161 !important;
  }
  [data-testid="stTabs"] [aria-selected="true"] {
    color: var(--wf-accent) !important;
    border-bottom-color: var(--wf-accent) !important;
  }
  [data-testid="stChatInput"] {
    border-color: var(--wf-border) !important;
  }
  hr {
    border-color: var(--wf-border) !important;
  }
  .wf-footnote {
    font-size: 0.75rem;
    color: var(--wf-muted);
    border-top: 1px dashed var(--wf-border);
    margin-top: 2rem;
    padding-top: 0.75rem;
  }
</style>
""",
        unsafe_allow_html=True,
    )


def card_open() -> None:
    st.markdown('<div class="wf-card">', unsafe_allow_html=True)


def card_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)
