"""个人中心 / 设置：对接真实后端 API。"""
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

API_BASE = KNOWLEDGE_BASE_CONFIG["api_base_url"].rstrip("/")


def _auth_headers() -> dict:
    token = st.session_state.get("auth_token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _fetch_profile():
    try:
        r = requests.get(f"{API_BASE}/profile", headers=_auth_headers(), timeout=10)
        if r.status_code == 200:
            st.session_state.user_profile = r.json()["user"]
        elif r.status_code == 401:
            st.session_state.authenticated = False
            st.session_state.auth_token = ""
            st.rerun()
    except requests.exceptions.ConnectionError:
        st.error("无法连接后端服务")


st.title("个人中心 / 设置")

# Ensure profile is loaded
if "user_profile" not in st.session_state:
    _fetch_profile()

user = st.session_state.get("user_profile", {})

sec = st.radio("设置分区", ["个人资料", "账号安全", "通知", "API 设置"], horizontal=True)

if sec == "个人资料":
    display_name = user.get("display_name", user.get("username", ""))
    email_val = user.get("email", "")
    bio_val = user.get("bio", "")

    with st.form("profile_form"):
        new_display = st.text_input("显示名", value=display_name)
        st.text_input("邮箱", value=email_val, disabled=True)
        new_bio = st.text_area("简介", value=bio_val, placeholder="介绍一下自己...")
        submitted = st.form_submit_button("保存修改")

    if submitted:
        try:
            body = {"display_name": new_display}
            if new_bio:
                body["bio"] = new_bio
            r = requests.put(
                f"{API_BASE}/profile", json=body, headers=_auth_headers(), timeout=10
            )
            if r.status_code == 200:
                st.session_state.user_profile = r.json()["user"]
                st.success("个人资料已保存")
            else:
                st.error(r.json().get("detail", "保存失败"))
        except requests.exceptions.ConnectionError:
            st.error("无法连接后端服务")

    # Avatar upload
    st.markdown("---")
    st.caption("头像上传")
    avatar_file = st.file_uploader("选择头像图片", type=["jpg", "jpeg", "png", "webp"])
    if avatar_file is not None:
        if st.button("上传头像"):
            try:
                files = {"file": (avatar_file.name, avatar_file.getvalue(), avatar_file.type)}
                r = requests.post(
                    f"{API_BASE}/profile/avatar",
                    files=files,
                    headers=_auth_headers(),
                    timeout=30,
                )
                if r.status_code == 200:
                    st.session_state.user_profile = r.json()["user"]
                    st.success("头像上传成功")
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "上传失败"))
            except requests.exceptions.ConnectionError:
                st.error("无法连接后端服务")

elif sec == "账号安全":
    with st.form("password_form"):
        st.text_input("当前密码", type="password", key="old_pw")
        st.text_input("新密码", type="password", key="new_pw")
        st.text_input("确认新密码", type="password", key="confirm_pw")
        submitted = st.form_submit_button("修改密码")

    if submitted:
        old = st.session_state.get("old_pw", "")
        new = st.session_state.get("new_pw", "")
        confirm = st.session_state.get("confirm_pw", "")
        if new != confirm:
            st.error("两次密码不一致")
        elif len(new) < 6:
            st.error("新密码长度不能少于 6 位")
        else:
            try:
                r = requests.put(
                    f"{API_BASE}/profile/password",
                    json={"old_password": old, "new_password": new},
                    headers=_auth_headers(),
                    timeout=10,
                )
                if r.status_code == 200:
                    st.success("密码修改成功")
                    st.info("请使用新密码重新登录。")
                else:
                    st.error(r.json().get("detail", "密码修改失败"))
            except requests.exceptions.ConnectionError:
                st.error("无法连接后端服务")

elif sec == "通知":
    prefs = user.get("preferences", {}) or {}
    email_notify = st.checkbox("邮件通知", value=prefs.get("email_notify", True))
    in_app_notify = st.checkbox("站内通知", value=prefs.get("in_app_notify", True))
    doc_alert = st.checkbox("文档处理提醒", value=prefs.get("doc_alert", True))
    video_alert = st.checkbox("视频分析提醒", value=prefs.get("video_alert", True))

    if st.button("保存通知设置"):
        try:
            new_prefs = {
                **prefs,
                "email_notify": email_notify,
                "in_app_notify": in_app_notify,
                "doc_alert": doc_alert,
                "video_alert": video_alert,
            }
            r = requests.put(
                f"{API_BASE}/profile",
                json={"preferences": new_prefs},
                headers=_auth_headers(),
                timeout=10,
            )
            if r.status_code == 200:
                st.session_state.user_profile = r.json()["user"]
                st.success("通知设置已保存")
            else:
                st.error(r.json().get("detail", "保存失败"))
        except requests.exceptions.ConnectionError:
            st.error("无法连接后端服务")

else:
    st.info("「API 设置」功能即将上线")
