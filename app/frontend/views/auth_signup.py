"""注册页：对接真实 /auth/register API。"""
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

st.title("注册")
st.caption("创建新账号以使用全部功能。")

with st.form("signup_form"):
    email = st.text_input("邮箱")
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")
    password2 = st.text_input("确认密码", type="password")
    submitted = st.form_submit_button("注册")

if submitted:
    if password != password2:
        st.error("两次密码不一致")
    elif len(password) < 6:
        st.error("密码长度不能少于 6 位")
    elif not username or not email:
        st.error("请填写所有字段")
    else:
        try:
            r = requests.post(
                f"{API_BASE}/auth/register",
                json={"username": username, "email": email, "password": password},
                timeout=10,
            )
            if r.status_code == 201:
                st.success("注册成功！请前往登录页面。")
                st.info("点击左侧导航「登录」进入。")
            elif r.status_code == 409:
                st.error(r.json().get("detail", "用户名或邮箱已被注册"))
            else:
                st.error(f"注册失败：{r.json().get('detail', '未知错误')}")
        except requests.exceptions.ConnectionError:
            st.error("无法连接后端服务，请检查 API 是否已启动。")
        except Exception as e:
            st.error(f"注册异常：{e}")
