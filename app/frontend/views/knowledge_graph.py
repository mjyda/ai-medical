from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_FRONTEND = _ROOT / "app" / "frontend"
if str(_FRONTEND) not in sys.path:
    sys.path.insert(0, str(_FRONTEND))

import streamlit as st

st.title("知识图谱")

st.caption("占位：未连接图数据库。优先尝试 Graphviz 渲染，失败则展示 DOT 源码。")

dot = """
digraph G {
  rankdir=LR;
  graph [bgcolor=transparent];
  node [shape=box, style=filled, fillcolor="#eeeeee", color="#757575", fontname="Helvetica"];
  edge [color="#9e9e9e"];
  LLM -> RAG;
  RAG -> VectorDB;
  LLM -> GPT;
  RAG -> LangChain;
  GPT -> Transformer;
}
"""

try:
    st.graphviz_chart(dot)
except Exception as exc:
    st.warning(f"Graphviz 不可用（{exc}）。以下为 DOT 源码：")
    st.code(dot.strip(), language="dot")

with st.expander("节点详情（Mock）"):
    st.write("选中节点：RAG")
    st.write("关联文档：`LangChain 介绍.pdf`、`faq.md`")
