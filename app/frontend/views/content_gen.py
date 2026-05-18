from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_FRONTEND = _ROOT / "app" / "frontend"
if str(_FRONTEND) not in sys.path:
    sys.path.insert(0, str(_FRONTEND))

import streamlit as st

st.title("内容生成")

c1, c2 = st.columns(2)
with c1:
    gen_type = st.selectbox("生成类型", ["学习笔记", "FAQ 摘要", "会议纪要", "测验题"])
    src = st.selectbox("来源文件（Mock）", ["Python 基础教程.pdf", "LangChain 介绍.pdf", "Deep Learning 笔记.md"])
with c2:
    desc = st.text_area("补充说明", height=120)

if st.button("开始生成（Mock）"):
    st.session_state.gen_result = (
        f"【{gen_type}】基于「{src}」的占位生成结果。\n\n"
        f"说明：{desc or '（无）'}\n\n此处为线稿骨架，未调用真实模型。"
    )

if st.session_state.get("gen_result"):
    st.subheader("生成结果")
    st.text_area("输出", value=st.session_state.gen_result, height=200)
    b1, b2 = st.columns(2)
    b1.button("复制（Mock）")
    b2.button("导出 Markdown（Mock）")
