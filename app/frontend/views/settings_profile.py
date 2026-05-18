from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_FRONTEND = _ROOT / "app" / "frontend"
if str(_FRONTEND) not in sys.path:
    sys.path.insert(0, str(_FRONTEND))

import streamlit as st

st.title("个人中心 / 设置")

sec = st.radio("设置分区", ["个人资料", "账号安全", "通知", "API 设置", "偏好"], horizontal=True)

if sec == "个人资料":
    display = st.session_state.get("user_display", "访客")
    with st.form("profile"):
        st.text_input("显示名", value=display)
        st.text_input("邮箱", value="user@example.com")
        st.text_area("简介", value="企业学习与内容管理用户。")
        if st.form_submit_button("保存（Mock）"):
            st.success("已保存（未写入后端）。")
else:
    st.info(f"「{sec}」为线稿占位，无实际逻辑。")
