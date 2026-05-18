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

st.title("视频详情")

BASE = KNOWLEDGE_BASE_CONFIG["api_base_url"].rstrip("/")


def _api_get(path: str, **kw):
    return requests.get(f"{BASE}{path}", timeout=kw.get("timeout", 15))


def _api_post(path: str, **kw):
    return requests.post(f"{BASE}{path}", timeout=kw.get("timeout", 120), **kw)


def _fmt_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


video_id = st.session_state.get("selected_video_id")
if not video_id:
    st.warning("未选择视频，请先在「视频库」页面点击「查看详情」。")
    st.stop()

try:
    r = _api_get(f"/videos/{video_id}")
    if r.status_code != 200:
        st.error(f"获取视频信息失败: {r.status_code}")
        st.stop()
    video = r.json()
except requests.RequestException as e:
    st.error(f"无法连接 API：{e}")
    st.stop()

st.subheader(video["original_filename"])

# 播放器 — Streamlit 服务端拉取视频字节（避免路径/URL歧义）
file_size = video.get("file_size", 0)
if file_size < 80 * 1024 * 1024:  # <80MB：直接加载字节播放
    with st.spinner("正在加载视频..."):
        try:
            vr = requests.get(f"{BASE}/videos/{video_id}/file", timeout=120)
            if vr.status_code == 200:
                st.video(vr.content, format="video/mp4")
            else:
                st.error(f"加载视频失败: {vr.status_code}")
        except requests.RequestException as e:
            st.error(f"无法连接 API：{e}")
else:
    # 超大文件回退到完整 URL（需浏览器可访问）
    st.video(f"http://127.0.0.1:8001/videos/{video_id}/file")

c1, c2, c3 = st.columns(3)
c1.metric("大小", _fmt_size(file_size))
dur = video.get("duration")
c2.metric("时长", f"{int(dur // 60)}:{int(dur % 60):02d}" if dur else "--")
c3.markdown(f"[下载视频](http://127.0.0.1:8001/videos/{video_id}/file)")

st.divider()
st.caption(f"文件 ID: {video_id}")
st.caption(f"状态: {video.get('status', '--')}  |  上传时间: {video.get('created_at', '--')}")

# ── AI 分析按钮 ──
if st.button("开始分析", type="primary", key=f"btn_analyze_{video_id}"):
    with st.spinner("正在进行 AI 分析，请稍候..."):
        try:
            ar = _api_post(f"/videos/{video_id}/analyze")
            if ar.status_code == 200:
                adata = ar.json()
                st.session_state["vid_related_docs"] = adata.get("related_documents", [])
                st.success("分析完成！")
                st.rerun()
            else:
                st.error(f"分析失败: {ar.json().get('detail', ar.text)}")
        except requests.RequestException as e:
            st.error(f"无法连接 API：{e}")

t1, t2, t3 = st.tabs(["摘要", "标签", "相关文档"])
with t1:
    summary = video.get("summary")
    if summary:
        st.markdown(summary)
    else:
        st.info("点击上方「开始分析」按钮生成 AI 摘要。")

with t2:
    tags = video.get("tags")
    if tags:
        tag_list = tags if isinstance(tags, list) else []
        if tag_list:
            cols = st.columns(len(tag_list))
            for i, tag in enumerate(tag_list):
                cols[i].markdown(f"`{tag}`")
    else:
        st.info("点击上方「开始分析」按钮生成 AI 标签。")

with t3:
    docs = st.session_state.get("vid_related_docs", [])
    if docs:
        for d in docs:
            doc_id = d.get("doc_id", "")
            snippet = d.get("snippet", "")
            score = d.get("score", 0)
            st.markdown(f"**相关度**: {score:.2%}")
            st.caption(snippet[:300])
            if doc_id:
                st.caption(f"文档 ID: `{doc_id}`")
            st.divider()
    else:
        st.info("点击上方「开始分析」按钮检索相关文档。")
