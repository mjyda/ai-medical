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

from app.config.config import KNOWLEDGE_BASE_CONFIG, SYSTEM_CONFIG

st.title("文档库")

BASE = KNOWLEDGE_BASE_CONFIG["api_base_url"].rstrip("/")


def _api_get(path: str, **kw):
    return requests.get(f"{BASE}{path}", timeout=kw.get("timeout", 15))


def _api_post(path: str, **kw):
    return requests.post(f"{BASE}{path}", timeout=kw.get("timeout", 120), **kw)


col_nav, col_main = st.columns([1, 4])
with col_nav:
    st.markdown("**分类**")
    st.radio("视图", ["全部文档", "我的文档", "共享", "回收站"], key="doc_cat_mock", label_visibility="collapsed")

with col_main:
    st.caption(f"知识库 API：`{BASE}`（请先 `uvicorn app.backend.api.main:app --port 8001`）")
    uploaded = st.file_uploader(
        "上传 PDF / DOCX（可多选）",
        type=["pdf", "docx"],
        accept_multiple_files=True,
    )
    if uploaded:
        if st.button("提交上传", type="primary"):
            files = []
            for uf in uploaded:
                files.append(
                    (
                        "files",
                        (uf.name, uf.getvalue(), "application/octet-stream"),
                    )
                )
            try:
                r = _api_post("/docs/upload", files=files)
                if r.status_code == 413:
                    st.error("文件过大（>100MB）")
                elif r.status_code != 200:
                    st.error(f"上传失败 {r.status_code}: {r.text}")
                else:
                    data = r.json()
                    items = data.get("items", [])
                    st.success(f"已上传 {len(items)} 个文件")
                    for it in items:
                        st.code(it)
            except requests.RequestException as e:
                st.error(f"无法连接 API：{e}")

    st.subheader("知识库中的文档（API）")
    try:
        lr = _api_get("/docs/")
        if lr.status_code != 200:
            st.warning(f"列表请求失败：{lr.status_code}")
            rows = []
        else:
            rows = lr.json().get("items", [])
    except requests.RequestException as e:
        st.warning(f"无法拉取文档列表（API 未启动？）：{e}")
        rows = []

    if rows:
        st.dataframe(
            [
                {
                    "doc_id": r["id"],
                    "文件名": r["filename"],
                    "状态": r["status"],
                    "分块数": r.get("chunk_count", 0),
                    "创建时间": str(r.get("created_at", "")),
                }
                for r in rows
            ],
            use_container_width=True,
            hide_index=True,
        )
        ids = [r["id"] for r in rows]
        pick = st.selectbox("选择文档", ids, format_func=lambda i: next((x["filename"] for x in rows if x["id"] == i), i))
        c1, c2, c3 = st.columns(3)
        if c1.button("打开详情"):
            st.session_state.selected_doc_id = pick
            st.success("请在侧栏进入「文档详情」。")
        if c2.button("排队解析"):
            try:
                pr = _api_post("/docs/parse", json={"doc_id": pick})
                st.info(pr.json() if pr.ok else pr.text)
            except requests.RequestException as e:
                st.error(str(e))
        if c3.button("排队向量化"):
            try:
                vr = _api_post("/docs/vectorize", json={"doc_id": pick})
                st.info(vr.json() if vr.ok else vr.text)
            except requests.RequestException as e:
                st.error(str(e))
    else:
        st.info("API 列表为空或未连接。")

    st.subheader("种子目录（本地 Markdown 等）")
    q = st.text_input("搜索", placeholder="按文件名搜索…", key="seed_q")
    doc_dir = _ROOT / SYSTEM_CONFIG["rag"]["document_dir"]
    seed_rows = []
    if doc_dir.is_dir():
        for p in sorted(doc_dir.iterdir()):
            if p.is_file():
                if q and q.lower() not in p.name.lower():
                    continue
                seed_rows.append(
                    {
                        "文件名": p.name,
                        "类型": p.suffix or "-",
                        "路径": str(p),
                    }
                )
    if seed_rows:
        st.dataframe(seed_rows, use_container_width=True, hide_index=True)
    else:
        st.caption("无本地种子文件或目录不存在。")
