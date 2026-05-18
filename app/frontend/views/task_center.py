from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_FRONTEND = _ROOT / "app" / "frontend"
if str(_FRONTEND) not in sys.path:
    sys.path.insert(0, str(_FRONTEND))

import streamlit as st

st.title("任务中心")

tab_all, tab_run, tab_ok, tab_fail = st.tabs(["全部", "进行中", "已完成", "失败"])
rows = [
    {"任务名": "文档解析 - faq.md", "类型": "解析", "状态": "进行中", "进度": 62, "创建时间": "2026-05-13 09:00"},
    {"任务名": "向量重建 - 全库", "类型": "索引", "状态": "已完成", "进度": 100, "创建时间": "2026-05-12 18:20"},
    {"任务名": "视频转写 - sample.mp4", "类型": "转写", "状态": "失败", "进度": 12, "创建时间": "2026-05-11 11:05"},
]

with tab_all:
    st.dataframe(rows, use_container_width=True, hide_index=True)
with tab_run:
    st.dataframe([r for r in rows if r["状态"] == "进行中"], use_container_width=True, hide_index=True)
with tab_ok:
    st.dataframe([r for r in rows if r["状态"] == "已完成"], use_container_width=True, hide_index=True)
with tab_fail:
    st.dataframe([r for r in rows if r["状态"] == "失败"], use_container_width=True, hide_index=True)
