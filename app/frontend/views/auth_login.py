"""登录页（线稿风）：对接真实 /auth/login API。"""
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
    if str(_repo) not in sys.path:
        sys.path.insert(0, str(_repo))
    _fe = _repo / "app" / "frontend"
    if str(_fe) not in sys.path:
        sys.path.insert(0, str(_fe))

import requests
import streamlit as st

from ui_theme import inject_wireframe_css
from app.config.config import KNOWLEDGE_BASE_CONFIG

API_BASE = KNOWLEDGE_BASE_CONFIG["api_base_url"].rstrip("/")

inject_wireframe_css()

st.markdown(
    """
<div style="max-width: 960px; margin: 0 auto;">
  <div style="font-size: 0.75rem; color: #616161; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.5rem;">Wireframe · 认证</div>
</div>
""",
    unsafe_allow_html=True,
)

left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown(
        """
<div style="background:#fafafa;border:1px solid #bdbdbd;border-radius:4px;min-height:320px;padding:1rem;color:#757575;font-size:0.85rem;">
  <strong>页面示意</strong><br/><br/>
  · 品牌区 / 插画占位<br/>
  · 灰度线框，无真实图片<br/>
  · 与线稿「登录」版式对齐
</div>
""",
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        """
<div style="background:#fff;border:1px solid #bdbdbd;border-radius:4px;padding:1.25rem 1.5rem;margin-bottom:1rem;">
  <h2 style="margin:0 0 0.25rem 0;color:#212121;font-size:1.25rem;">登录</h2>
  <p style="margin:0;color:#616161;font-size:0.9rem;">对接后端认证服务。</p>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("用户名", placeholder="请输入用户名")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        submitted = st.form_submit_button("登录", type="primary", use_container_width=True)

    if submitted:
        if not username or not password:
            st.error("请输入用户名和密码")
        else:
            try:
                r = requests.post(
                    f"{API_BASE}/auth/login",
                    json={"username": username, "password": password},
                    timeout=10,
                )
                if r.status_code == 200:
                    data = r.json()
                    st.session_state.authenticated = True
                    st.session_state.auth_token = data["token"]
                    st.session_state.user_profile = data["user"]
                    st.session_state.user_display = data["user"].get("display_name") or data["user"].get("username", "访客")
                    st.rerun()
                elif r.status_code == 401:
                    st.error("用户名或密码错误")
                else:
                    st.error(f"登录失败：{r.json().get('detail', '未知错误')}")
            except requests.exceptions.ConnectionError:
                st.error("无法连接后端服务，请检查 API 是否已启动。")
            except Exception as e:
                st.error(f"登录异常：{e}")

    if st.button("跳过登录（仅本地开发）", use_container_width=True, help="直接进入工作台，便于调试其它页面"):
        st.session_state.authenticated = True
        st.session_state.user_display = "dev"
        st.session_state.remember_me = False
        st.rerun()

    st.markdown("---")
    st.caption("第三方登录（占位）")
    c1, c2, c3 = st.columns(3)
    c1.button("微信", disabled=True, use_container_width=True)
    c2.button("企业微信", disabled=True, use_container_width=True)
    c3.button("钉钉", disabled=True, use_container_width=True)
