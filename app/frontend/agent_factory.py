"""Single cached MedicalChatAgent instance for all Streamlit pages."""
from pathlib import Path
import sys

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st


@st.cache_resource
def get_medical_agent():
    from app.backend.agents.medical_chat_agent import MedicalChatAgent

    return MedicalChatAgent()
