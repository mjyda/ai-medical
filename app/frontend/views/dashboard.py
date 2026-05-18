from pathlib import Path
import sys

_here = Path(__file__).resolve().parent
_repo = None
for _root in _here.parents:
    if (_root / "main.py").is_file() and (_root / "app").is_dir():
        if str(_root) not in sys.path:
            sys.path.insert(0, str(_root))
        _fe = _root / "app" / "frontend"
        if str(_fe) not in sys.path:
            sys.path.insert(0, str(_fe))
        _repo = _root
        break

if _repo is None:
    _repo = Path(__file__).resolve().parents[3]

_ROOT = _repo

import streamlit as st

from app.config.config import SYSTEM_CONFIG
from ui_theme import inject_wireframe_css

inject_wireframe_css()

st.title("首页 / 仪表盘")

doc_dir = _ROOT / SYSTEM_CONFIG["rag"]["document_dir"]
n_docs = len([p for p in doc_dir.iterdir() if p.is_file()]) if doc_dir.is_dir() else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("文档总数", n_docs)
with c2:
    st.metric("提问次数（Mock）", 56)
with c3:
    st.metric("积分（Mock）", 312)
with c4:
    st.metric("进行中任务（Mock）", 8)

st.subheader("最近使用")
rows = []
if doc_dir.is_dir():
    for p in sorted(doc_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
        if p.is_file():
            rows.append({"文件名": p.name, "类型": p.suffix or "-", "大小(KB)": round(p.stat().st_size / 1024, 1)})
if rows:
    st.dataframe(rows, use_container_width=True, hide_index=True)
else:
    st.info("暂无文档")

st.subheader("最近提问（Mock）")
st.dataframe(
    [
        {"时间": "2026-05-12 10:01", "问题": "智能客服支持哪些渠道？"},
        {"时间": "2026-05-11 16:22", "问题": "业务流程是怎样的？"},
    ],
    use_container_width=True,
    hide_index=True,
)
