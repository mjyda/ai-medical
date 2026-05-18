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

st.title("视频库")

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


def _refresh_list():
    try:
        r = _api_get("/videos/")
        if r.status_code == 200:
            data = r.json()
            st.session_state["video_rows"] = data.get("items", [])
        else:
            st.session_state["video_rows"] = []
    except requests.RequestException:
        st.session_state["video_rows"] = []


def _show_video_detail(video_id: str):
    """内嵌展示视频详情：播放器 + 元数据。"""
    try:
        r = _api_get(f"/videos/{video_id}")
        if r.status_code != 200:
            st.error(f"获取视频信息失败: {r.status_code}")
            return
        video = r.json()
    except requests.RequestException as e:
        st.error(f"无法连接 API：{e}")
        return

    st.subheader(video["original_filename"])

    # 播放器 — 由 Streamlit 服务端拉取视频字节，通过 WebSocket 推给浏览器
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
    c3.markdown(f"[下载视频](/api/videos/{video_id}/file)")

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


col_nav, col_main = st.columns([1, 4])
with col_nav:
    st.markdown("**分类**")
    st.radio("视图", ["全部视频", "我的上传", "共享"], key="vid_cat")

with col_main:
    st.caption(f"视频 API：`{BASE}/videos`")

    # ── 在线下载 ──
    with st.expander("🌐 在线下载（B站 / 抖音 / YouTube 等）", expanded=False):
        dl_url = st.text_input("视频链接", placeholder="https://...")
        col_q1, col_q2, col_q3 = st.columns([1, 1, 2])
        with col_q1:
            quality = st.selectbox("最高清晰度", [1080, 720, 480, 360], index=0,
                                   format_func=lambda q: f"{q}p")
        with col_q2:
            st.caption("")  # spacer
            st.caption("")
            do_dl = st.button("开始下载", type="primary", key="btn_download")
        with col_q3:
            if do_dl:
                if not dl_url.strip():
                    st.error("请输入视频链接")
                else:
                    with st.spinner("正在下载，请稍候..."):
                        try:
                            r = _api_post(
                                "/videos/download",
                                json={"url": dl_url.strip(), "max_height": quality},
                            )
                            if r.status_code == 400:
                                st.error(f"下载失败: {r.json().get('detail', r.text)}")
                            elif r.status_code != 200:
                                st.error(f"下载失败 {r.status_code}: {r.text}")
                            else:
                                data = r.json()
                                dur = data.get("duration")
                                dur_str = f" | {int(dur // 60)}:{int(dur % 60):02d}" if dur else ""
                                st.success(f"下载完成: {data['filename']} ({_fmt_size(data['file_size'])}{dur_str})")
                                _refresh_list()
                                st.rerun()
                        except requests.RequestException as e:
                            st.error(f"无法连接 API：{e}")
        st.caption("支持 B站、抖音、YouTube、TikTok 等主流网站，最高 1080p。下载为 MP4 格式。")

    # ── 本地上传 ──
    with st.expander("📤 本地上传", expanded=False):
        uploaded = st.file_uploader(
            "选择视频文件（MP4 / AVI / MOV / MKV / WebM）",
            type=["mp4", "avi", "mov", "mkv", "webm"],
            accept_multiple_files=False,
        )
        if uploaded:
            if st.button("提交上传", type="primary"):
                try:
                    r = _api_post(
                        "/videos/upload",
                        files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")},
                    )
                    if r.status_code == 413:
                        st.error("文件过大（>500MB）")
                    elif r.status_code == 400:
                        st.error(f"格式不支持: {r.text}")
                    elif r.status_code != 200:
                        st.error(f"上传失败 {r.status_code}: {r.text}")
                    else:
                        data = r.json()
                        st.success(f"已上传: {data.get('filename', '')} ({_fmt_size(data.get('file_size', 0))})")
                        st.rerun()
                except requests.RequestException as e:
                    st.error(f"无法连接 API：{e}")

    st.subheader("视频列表")
    if "video_rows" not in st.session_state:
        _refresh_list()
    rows = st.session_state.get("video_rows", [])

    if rows:
        st.dataframe(
            [
                {
                    "文件名": r["original_filename"],
                    "大小": _fmt_size(r.get("file_size", 0)),
                    "状态": r["status"],
                    "上传时间": str(r.get("created_at", "")),
                }
                for r in rows
            ],
            use_container_width=True,
            hide_index=True,
        )
        ids = [r["id"] for r in rows]
        pick = st.selectbox(
            "选择视频",
            ids,
            format_func=lambda i: next((x["original_filename"] for x in rows if x["id"] == i), i),
        )
        if st.button("查看详情", type="primary"):
            st.session_state.selected_video_id = pick
            st.rerun()

        # ── 视频详情内嵌展示 ──
        selected_id = st.session_state.get("selected_video_id")
        if selected_id:
            st.divider()
            _show_video_detail(selected_id)
    else:
        st.info("暂无视频，请上传。")
