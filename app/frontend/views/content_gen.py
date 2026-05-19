from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_FRONTEND = _ROOT / "app" / "frontend"
if str(_FRONTEND) not in sys.path:
    sys.path.insert(0, str(_FRONTEND))

import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage

from app.backend.repositories.kb_document_repository import KBDocumentRepository

import agent_factory

GEN_PROMPTS = {
    "学习笔记": (
        "你是一位专业的学习助手。请根据以下文档内容生成一份结构清晰的学习笔记。"
        "包含：标题、关键概念、核心知识点（分条列出）、总结。使用Markdown格式。"
    ),
    "FAQ 摘要": (
        "你是一位知识管理专家。请根据以下文档内容生成一份FAQ常见问题摘要。"
        "提取5-10个最可能被问到的问题，并给出简明解答。使用Markdown格式。"
    ),
    "会议纪要": (
        "你是一位专业的会议记录员。请根据以下文档内容，提炼信息并模拟生成一份会议纪要。"
        "包含：会议主题、要点摘要、决议事项、待办任务。使用Markdown格式。"
    ),
    "测验题": (
        "你是一位教育培训专家。请根据以下文档内容生成一套测验题。"
        "包含5道选择题（每题4个选项，标注正确答案）和3道简答题（附参考答案）。使用Markdown格式。"
    ),
}

MAX_DOC_CHARS = 12000


@st.cache_data(ttl=30, show_spinner=False)
def _list_vectorized_docs():
    try:
        repo = KBDocumentRepository()
        docs = repo.list_recent(200)
        return {d["filename"]: d for d in docs if d["status"] in ("vectorized", "parsed")}
    except Exception:
        return {}


@st.cache_data(ttl=30, show_spinner=False)
def _get_doc_text(doc_id: str):
    try:
        repo = KBDocumentRepository()
        doc = repo.get_by_id(doc_id)
        if doc and doc.get("parsed_text"):
            return doc["parsed_text"]
    except Exception:
        pass
    return None


st.title("内容生成")

agent = agent_factory.get_medical_agent()
doc_map = _list_vectorized_docs()

c1, c2 = st.columns(2)
with c1:
    gen_type = st.selectbox("生成类型", list(GEN_PROMPTS.keys()))

    doc_names = list(doc_map.keys())
    if doc_names:
        selected_doc = st.selectbox("来源文件", doc_names)
    else:
        st.warning("暂无已解析的文档，请先在「文档库」上传并完成解析")
        selected_doc = None

with c2:
    desc = st.text_area(
        "补充说明（可选）",
        height=120,
        placeholder="例如：请用中文生成，重点总结第三章节…",
    )

if "gen_result" not in st.session_state:
    st.session_state.gen_result = ""

disabled = not doc_names or selected_doc is None
if st.button("开始生成", type="primary", disabled=disabled, use_container_width=True):
    doc = doc_map[selected_doc]
    doc_text = _get_doc_text(doc["id"])

    if not doc_text:
        st.error("该文档尚未完成解析，请先在文档库中点击「排队解析」")
    else:
        if len(doc_text) > MAX_DOC_CHARS:
            doc_text = doc_text[:MAX_DOC_CHARS] + "\n\n> ⚠ 文档过长，已自动截断前 {} 字符".format(MAX_DOC_CHARS)

        system_prompt = GEN_PROMPTS[gen_type]
        if desc:
            system_prompt += f"\n\n补充要求：{desc}"
        system_prompt += "\n\n请严格按照要求输出，不要添加额外客套话。"

        user_prompt = f"文档名称：{doc['filename']}\n\n文档内容：\n{doc_text}"

        with st.spinner("正在生成…"):
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
            full = ""
            placeholder = st.empty()
            try:
                for chunk in agent.llm.stream(messages):
                    if hasattr(chunk, "content") and chunk.content:
                        full += chunk.content
                        placeholder.markdown(full + "▌")
                placeholder.markdown(full)
                st.session_state.gen_result = full
            except Exception as e:
                st.error(f"生成失败：{e}")

if st.session_state.gen_result:
    st.divider()
    st.subheader("生成结果")

    st.text_area(
        "输出内容（可直接选中复制）",
        value=st.session_state.gen_result,
        height=350,
        disabled=False,
        key="gen_output",
    )

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "导出 Markdown",
            data=st.session_state.gen_result,
            file_name=f"{(gen_type)}_{(selected_doc or 'output')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with c2:
        if st.button("重新生成", use_container_width=True):
            st.session_state.gen_result = ""
            st.rerun()
