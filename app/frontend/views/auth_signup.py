from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_FRONTEND = _ROOT / "app" / "frontend"
if str(_FRONTEND) not in sys.path:
    sys.path.insert(0, str(_FRONTEND))

import streamlit as st

st.title("注册")
st.caption("占位页：不写入数据库，提交后仅提示成功。")

with st.form("signup_form"):
    email = st.text_input("邮箱")
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")
    password2 = st.text_input("确认密码", type="password")
    submitted = st.form_submit_button("注册")

if submitted:
    if password != password2:
        st.error("两次密码不一致")
    else:
        st.success("注册成功（Mock）。请从侧栏进入「登录」。")
