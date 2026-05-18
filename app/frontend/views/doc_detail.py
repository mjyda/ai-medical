from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_FRONTEND = _ROOT / "app" / "frontend"
if str(_FRONTEND) not in sys.path:
    sys.path.insert(0, str(_FRONTEND))

import requests
import streamlit as st

from app.config.config import KNOWLEDGE_BASE_CONFIG

st.title("文档详情")

BASE = KNOWLEDGE_BASE_CONFIG["api_base_url"].rstrip("/")

doc_id = st.session_state.get("selected_doc_id")
if not doc_id:
    manual = st.text_input("输入 doc_id（UUID）", placeholder="从文档库上传或列表复制")
    if manual and st.button("加载"):
        st.session_state.selected_doc_id = manual.strip()
        st.rerun()
    st.stop()

try:
    r = requests.get(f"{BASE}/docs/{doc_id}", timeout=15)
except requests.RequestException as e:
    st.error(f"无法连接 API：{e}")
    st.stop()

if r.status_code == 404:
    st.error("文档不存在")
    st.stop()
if r.status_code != 200:
    st.error(f"请求失败 {r.status_code}: {r.text}")
    st.stop()

row = r.json()
st.subheader(row.get("filename", doc_id))
st.write(f"**状态**：{row.get('status')}")
st.write(f"**分块数**：{row.get('chunk_count', 0)}")
if row.get("error_message"):
    st.error(row["error_message"][:4000])

tab_preview, tab_meta = st.tabs(["解析正文预览", "元数据"])
with tab_preview:
    text = row.get("parsed_text") or ""
    if text:
        st.text_area("parsed_text", value=text[:50_000], height=400, disabled=True)
    else:
        st.info("暂无解析正文；请在文档库点击「排队解析」或等待 Celery 完成。")
with tab_meta:
    st.json({k: v for k, v in row.items() if k != "parsed_text"})

if st.button("清除选择"):
    st.session_state.pop("selected_doc_id", None)
    st.rerun()
