"""Streamlit entry: wireframe multipage app via st.navigation + st.Page."""
from pathlib import Path

import streamlit as st

import _paths

_paths.ensure_repo_root()

from ui_theme import inject_wireframe_css

st.set_page_config(
    page_title="AI 学习与内容管理平台",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_wireframe_css()

# 必须使用基于入口文件的绝对路径：st.Page 按进程 cwd 解析相对路径，
# 从 IDE / 其它目录启动时 app/frontend/views/... 会找不到。
_VIEWS_DIR = Path(__file__).resolve().parent / "views"


def vp(name: str) -> str:
    return str((_VIEWS_DIR / name).resolve())


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

with st.sidebar:
    st.markdown("### AI 学习与内容管理")
    st.caption("线稿风骨架 · 侧栏导航（Streamlit 无原生底部 Dock）")
    if st.session_state.authenticated:
        u = st.session_state.get("user_display", "访客")
        st.caption(f"用户：{u}")
        if st.button("退出登录", type="primary"):
            st.session_state.authenticated = False
            for k in (
                "user_display", "auth_token", "user_profile",
                "messages", "session_id", "gen_result",
                "selected_doc", "selected_doc_id",
                "selected_video", "selected_video_id",
            ):
                st.session_state.pop(k, None)
            st.rerun()

if not st.session_state.authenticated:
    pages = {
        "认证": [
            st.Page(vp("auth_login.py"), title="登录", icon="🔐", default=True),
            st.Page(vp("auth_signup.py"), title="注册", icon="📝"),
        ]
    }
else:
    pages = {
        "工作台": [
            st.Page(vp("dashboard.py"), title="首页", icon="🏠", default=True),
        ],
        "资源": [
            st.Page(vp("doc_library.py"), title="文档库", icon="📂"),
            st.Page(vp("doc_detail.py"), title="文档详情", icon="📄"),
            st.Page(vp("video_library.py"), title="视频库", icon="🎬"),
            st.Page(vp("video_detail.py"), title="视频详情", icon="🎥"),
        ],
        "AI 功能": [
            st.Page(vp("chat_qa.py"), title="智能问答", icon="💬"),
            st.Page(vp("content_gen.py"), title="内容生成", icon="✨"),
        ],
        "系统": [
            st.Page(vp("task_center.py"), title="任务中心", icon="✅"),
            st.Page(vp("knowledge_graph.py"), title="知识图谱", icon="🗺️"),
            st.Page(vp("settings_profile.py"), title="个人中心", icon="👤"),
        ],
    }

pg = st.navigation(pages, position="sidebar")
pg.run()

st.markdown(
    '<p class="wf-footnote">底部全局导航在 Streamlit 1.36 中无等价组件；'
    "请使用左侧分组导航。程序化切换页面能力有限，故未做无效底部按钮。</p>",
    unsafe_allow_html=True,
)
