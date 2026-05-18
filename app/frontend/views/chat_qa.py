from pathlib import Path
import sys
import uuid

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_FRONTEND = _ROOT / "app" / "frontend"
if str(_FRONTEND) not in sys.path:
    sys.path.insert(0, str(_FRONTEND))

import streamlit as st

import agent_factory

st.title("智能问答")

agent = agent_factory.get_medical_agent()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("当前会话")
    st.caption(st.session_state.session_id[:12] + "…")
    if st.button("新对话"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("历史会话")
    sessions = agent.get_all_sessions()
    if sessions:
        for session in sessions:
            with st.expander(session.get("title", "会话")[:24]):
                st.caption(f"消息 {session.get('message_count', 0)} · {session.get('last_updated', '')}")
                c1, c2 = st.columns(2)
                if c1.button("加载", key=f"ld_{session['memory_id']}"):
                    st.session_state.session_id = session["memory_id"]
                    st.session_state.messages = agent.load_session(session["memory_id"])
                    st.rerun()
                if c2.button("删除", key=f"dl_{session['memory_id']}"):
                    agent.delete_session(session["memory_id"])
                    st.rerun()
    else:
        st.caption("暂无历史")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("请输入问题…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full = ""
        for chunk in agent.stream_chat(st.session_state.session_id, prompt):
            full += chunk
            placeholder.markdown(full + "▌")
        placeholder.markdown(full)

    st.session_state.messages.append({"role": "assistant", "content": full})

    sources = agent.get_last_sources()
    if sources:
        with st.expander("引用文档 / 来源", expanded=True):
            for s in sources:
                st.markdown(f"- {s}")

st.divider()
with st.expander("产品咨询（占位）", expanded=False):
    st.write("与线稿一致的可折叠表单区；提交不落库。")
    with st.form("lead"):
        n = st.text_input("姓名")
        e = st.text_input("邮箱")
        if st.form_submit_button("提交"):
            st.success("已记录（Mock）")
