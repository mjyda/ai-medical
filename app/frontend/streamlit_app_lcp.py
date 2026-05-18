import streamlit as st
import uuid

import _paths

_paths.ensure_repo_root()

# 优化Streamlit配置
# 移除不存在的配置选项
st.set_option('client.showErrorDetails', False)


# 缓存AI代理实例，避免重复初始化
@st.cache_resource
def get_agent():
    """获取AI代理实例（缓存）"""
    from app.backend.agents.medical_chat_agent import MedicalChatAgent
    return MedicalChatAgent()


# 缓存会话历史数据
@st.cache_data(ttl=120)  # 缓存120秒
def get_all_sessions():
    """获取所有会话历史（缓存）"""
    agent = get_agent()
    return agent.get_all_sessions()


# 设置页面标题和图标（最小化配置）
st.set_page_config(
    page_title="智能小助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"  # 默认折叠侧边栏
)

# 初始化会话状态
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'sessions_loaded' not in st.session_state:
    st.session_state.sessions_loaded = False

if 'sidebar_expanded' not in st.session_state:
    st.session_state.sidebar_expanded = False

# 主界面 - 优先渲染关键内容
# 1. 首先渲染页面标题和核心功能
st.title("🤖 智能小助手 - 企业客服系统")

# 2. 显示聊天历史（核心功能）
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. 聊天输入（核心功能）
if prompt := st.chat_input("请输入您的问题..."):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 显示AI正在输入
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # 调用AI代理，使用流式输出
        agent = get_agent()
        for chunk in agent.stream_chat(st.session_state.session_id, prompt):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")

        # 显示完整回复
        message_placeholder.markdown(full_response)

    # 添加AI回复到历史
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 清除会话缓存，确保下次获取最新数据
    get_all_sessions.clear()

# 4. 分隔线
st.markdown("---")

# 5. 延迟渲染非关键组件
with st.expander("📋 产品咨询", expanded=False):
    with st.form("product_consultation_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("姓名")
            email = st.text_input("邮箱")
            phone = st.text_input("电话")

        with col2:
            product = st.selectbox("产品类型", ["智能客服系统", "智能办公自动化", "数据分析与决策支持", "企业数字化转型咨询"])
            message = st.text_area("咨询内容")

        submit_button = st.form_submit_button("提交咨询")

        if submit_button:
            if not name or not email or not phone or not product or not message:
                st.error("请填写所有必填信息")
            else:
                st.success("咨询提交成功，我们会尽快与您联系！")

with st.expander("🛠️ 服务申请", expanded=False):
    with st.form("service_application_form"):
        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input("公司名称")
            contact_person = st.text_input("联系人")
            contact_phone = st.text_input("联系电话")

        with col2:
            service_type = st.selectbox("服务类型", ["智能客服系统实施", "智能办公自动化实施", "数据分析与决策支持实施", "企业数字化转型咨询"])
            service_date = st.date_input("期望服务日期")

        submit_button = st.form_submit_button("提交申请")

        if submit_button:
            if not company_name or not contact_person or not contact_phone or not service_type:
                st.error("请填写所有必填信息")
            else:
                st.success("服务申请提交成功，我们会尽快与您联系！")

with st.expander("📞 联系我们", expanded=False):
    st.write("**总部地址：** 北京市海淀区中关村科技园区")
    st.write("**联系电话：** 400-123-4567")
    st.write("**官方网站：** www.wootion.com")
    st.write("**邮箱：** wootion@example.com")

# 侧边栏 - 延迟加载，只在展开时显示
with st.sidebar:
    # 最小化SVG图标
    st.markdown("""
    <div style="text-align: center; margin-bottom: 15px;">
        <svg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
            <circle cx="40" cy="40" r="35" fill="#4CAF50"/>
            <text x="40" y="45" font-size="30" text-anchor="middle" fill="white">🤖</text>
        </svg>
    </div>
    """, unsafe_allow_html=True)

    st.title("智能小助手")
    st.write("企业客服系统")

    # 会话管理
    st.write(f"会话ID: {st.session_state.session_id[:8]}...")

    if st.button("开始新会话"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        get_all_sessions.clear()
        st.rerun()

    # 聊天历史 - 延迟加载
    st.markdown("---")
    st.subheader("历史会话")

    # 刷新按钮
    if st.button("刷新列表"):
        get_all_sessions.clear()
        st.session_state.sessions_loaded = False
        st.rerun()

    # 只在需要时加载会话列表
    if not st.session_state.sessions_loaded:
        st.write("加载会话列表...")
        st.session_state.sessions_loaded = True
        st.rerun()
    else:
        try:
            sessions = get_all_sessions()

            if sessions:
                for session in sessions:
                    with st.expander(f"{session['title'][:30]}..."):
                        st.write(f"消息数: {session['message_count']}")
                        st.write(f"最后更新: {session['last_updated']}")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"加载", key=f"load_{session['memory_id']}"):
                                st.session_state.session_id = session['memory_id']
                                agent = get_agent()
                                st.session_state.messages = agent.load_session(session['memory_id'])
                                st.rerun()
                        with col2:
                            if st.button(f"删除", key=f"delete_{session['memory_id']}"):
                                agent = get_agent()
                                agent.delete_session(session['memory_id'])
                                get_all_sessions.clear()
                                st.session_state.sessions_loaded = False
                                st.rerun()
            else:
                st.write("暂无历史会话")
        except Exception as e:
            st.write("加载会话失败")
