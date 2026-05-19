from pathlib import Path
import sys
import time

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_FRONTEND = _ROOT / "app" / "frontend"
if str(_FRONTEND) not in sys.path:
    sys.path.insert(0, str(_FRONTEND))

import requests
import streamlit as st

from app.backend.repositories.kb_document_repository import KBDocumentRepository
from app.backend.repositories.video_repository import VideoRepository
from app.config.config import KNOWLEDGE_BASE_CONFIG

API_BASE = KNOWLEDGE_BASE_CONFIG["api_base_url"].rstrip("/")

STATUS = {
    "uploaded": {"label": "待处理", "category": "queued", "progress": 10},
    "parsing": {"label": "解析中", "category": "running", "progress": 30},
    "parsed": {"label": "待向量化", "category": "queued", "progress": 50},
    "vectorizing": {"label": "向量化中", "category": "running", "progress": 75},
    "vectorized": {"label": "已完成", "category": "done", "progress": 100},
    "failed": {"label": "失败", "category": "failed", "progress": 0},
}

SOURCE_CATEGORY = {"docs": "文档解析", "videos": "视频转写"}


@st.cache_data(ttl=5, show_spinner=False)
def _fetch_all_tasks():
    tasks = []
    try:
        repo = KBDocumentRepository()
        for d in repo.list_recent(200):
            s = STATUS.get(d["status"], {"label": d["status"], "category": "unknown", "progress": 0})
            tasks.append({
                "id": d["id"],
                "name": f"文档处理 - {d['filename']}",
                "type": "文档解析",
                "status": d["status"],
                "status_label": s["label"],
                "category": s["category"],
                "progress": s["progress"],
                "created_at": str(d.get("created_at", ""))[:19],
                "filename": d["filename"],
                "error": (d.get("error_message") or "") if d["status"] == "failed" else "",
                "source": "docs",
            })
    except Exception:
        pass

    try:
        repo = VideoRepository()
        for v in repo.list_recent(200):
            s = STATUS.get(v["status"], {"label": v["status"], "category": "unknown", "progress": 0})
            tasks.append({
                "id": v["id"],
                "name": f"视频处理 - {v['original_filename']}",
                "type": "视频转写",
                "status": v["status"],
                "status_label": s["label"],
                "category": s["category"],
                "progress": s["progress"],
                "created_at": str(v.get("created_at", ""))[:19],
                "filename": v["original_filename"],
                "error": (v.get("error_message") or "") if v["status"] == "failed" else "",
                "source": "videos",
            })
    except Exception:
        pass

    tasks.sort(key=lambda t: t["created_at"], reverse=True)
    return tasks


def _api_parse(doc_id: str):
    try:
        return requests.post(f"{API_BASE}/docs/parse", json={"doc_id": doc_id}, timeout=10)
    except requests.RequestException as e:
        st.error(f"API 请求失败: {e}")
        return None


def _api_vectorize(doc_id: str):
    try:
        return requests.post(f"{API_BASE}/docs/vectorize", json={"doc_id": doc_id}, timeout=10)
    except requests.RequestException as e:
        st.error(f"API 请求失败: {e}")
        return None


def _api_delete(source: str, item_id: str):
    try:
        return requests.delete(f"{API_BASE}/{source}/{item_id}", timeout=10)
    except requests.RequestException as e:
        st.error(f"API 请求失败: {e}")
        return None


def _render_task_row(task: dict, prefix: str = ""):
    cols = st.columns([4, 1, 1.2, 1.2, 1.5, 2])
    with cols[0]:
        st.markdown(f"**{task['name']}**")
        if task.get("error"):
            st.caption(f"⚠ {task['error'][:120]}")
    with cols[1]:
        st.caption(task["type"])
    with cols[2]:
        color = {"running": "blue", "done": "green", "failed": "red", "queued": "orange"}.get(task["category"], "grey")
        st.markdown(f":{color}[{task['status_label']}]")
    with cols[3]:
        st.progress(task["progress"] / 100)
    with cols[4]:
        st.caption(task["created_at"])
    with cols[5]:
        btns = st.columns(2)
        if task["source"] == "docs":
            if task["status"] == "uploaded":
                if btns[0].button("解析", key=f"{prefix}parse_{task['id']}", use_container_width=True):
                    r = _api_parse(task["id"])
                    if r is not None and r.status_code == 200:
                        st.success("已触发解析")
                        time.sleep(0.5)
                        st.rerun()
                    elif r is not None:
                        st.error(f"触发失败: {r.text}")
            elif task["status"] == "parsed":
                if btns[0].button("向量化", key=f"{prefix}vec_{task['id']}", use_container_width=True):
                    r = _api_vectorize(task["id"])
                    if r is not None and r.status_code == 200:
                        st.success("已触发向量化")
                        time.sleep(0.5)
                        st.rerun()
                    elif r is not None:
                        st.error(f"触发失败: {r.text}")
            elif task["status"] == "failed":
                if btns[0].button("重试", key=f"{prefix}retry_{task['id']}", use_container_width=True):
                    r = _api_parse(task["id"])
                    if r is not None and r.status_code == 200:
                        st.success("已重新触发解析")
                        time.sleep(0.5)
                        st.rerun()
                    elif r is not None:
                        st.error(f"触发失败: {r.text}")
            else:
                btns[0].caption("")
        else:
            btns[0].caption("")

        if btns[1].button("删除", key=f"{prefix}del_{task['id']}", use_container_width=True):
            r = _api_delete(task["source"], task["id"])
            if r is not None and r.status_code == 200:
                st.success("已删除")
                time.sleep(0.5)
                st.rerun()
            elif r is not None:
                st.error(f"删除失败: {r.text}")


def _render_task_list(task_list: list, _label: str):
    if not task_list:
        st.info("暂无任务")
        return

    for task in task_list:
        _render_task_row(task, prefix=_label)


# ── Main UI ──

st.title("任务中心")

tasks = _fetch_all_tasks()

# Stats
total = len(tasks)
running_count = sum(1 for t in tasks if t["category"] == "running")
queued_count = sum(1 for t in tasks if t["category"] == "queued")
done_count = sum(1 for t in tasks if t["category"] == "done")
failed_count = sum(1 for t in tasks if t["category"] == "failed")

cols = st.columns(5)
with cols[0]:
    st.metric("全部任务", total)
with cols[1]:
    st.metric("进行中", running_count)
with cols[2]:
    st.metric("排队中", queued_count)
with cols[3]:
    st.metric("已完成", done_count)
with cols[4]:
    st.metric("失败", failed_count)

st.divider()

c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    if st.button("手动刷新", use_container_width=True):
        _fetch_all_tasks.clear()
        st.rerun()
with c2:
    auto = st.checkbox("自动刷新", value=False)

tab_all, tab_run, tab_queued, tab_ok, tab_fail = st.tabs([
    f"全部 ({total})",
    f"进行中 ({running_count})",
    f"排队中 ({queued_count})",
    f"已完成 ({done_count})",
    f"失败 ({failed_count})",
])

with tab_all:
    _render_task_list(tasks, "全部")
with tab_run:
    _render_task_list([t for t in tasks if t["category"] == "running"], "进行中")
with tab_queued:
    _render_task_list([t for t in tasks if t["category"] == "queued"], "排队中")
with tab_ok:
    _render_task_list([t for t in tasks if t["category"] == "done"], "已完成")
with tab_fail:
    _render_task_list([t for t in tasks if t["category"] == "failed"], "失败")

if auto:
    time.sleep(10)
    st.rerun()
