import streamlit as st
import uuid
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
print(f"Added to path: {project_root}")
print(f"Python path: {sys.path}")

from app.backend.agents.xiaozhi_agent import XiaozhiAgent

# 初始化AI代理
agent = XiaozhiAgent()

# 设置页面标题和图标
st.set_page_config(
    page_title="智能小助手 - 企业客服系统",
    page_icon="🤖",
    layout="wide"
)

# 侧边栏
with st.sidebar:
    st.image("https://via.placeholder.com/150", width=150)
    st.title("智能小助手")
    st.write("企业智能客服系统")
    
    # 会话管理
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    st.write(f"会话ID: {st.session_state.session_id}")
    
    if st.button("开始新会话"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    
    # 聊天历史
    st.markdown("---")
    st.subheader("历史会话")
    
    # 获取所有会话历史
    sessions = agent.get_all_sessions()
    
    if sessions:
        for session in sessions:
            with st.expander(f"{session['title']}"):
                st.write(f"消息数: {session['message_count']}")
                st.write(f"最后更新: {session['last_updated']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"加载会话", key=f"load_{session['memory_id']}"):
                        st.session_state.session_id = session['memory_id']
                        st.session_state.messages = agent.load_session(session['memory_id'])
                        st.rerun()
                with col2:
                    if st.button(f"删除会话", key=f"delete_{session['memory_id']}"):
                        agent.delete_session(session['memory_id'])
                        st.rerun()
    else:
        st.write("暂无历史会话")

# 主界面
st.title("🤖 智能小助手 - 企业客服系统")

# 初始化消息历史
if 'messages' not in st.session_state:
    st.session_state.messages = []

# 显示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 聊天输入
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
        for chunk in agent.stream_chat(st.session_state.session_id, prompt):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        
        # 显示完整回复
        message_placeholder.markdown(full_response)
    
    # 添加AI回复到历史
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# 产品咨询表单
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

# 服务申请表单
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

# 联系我们
with st.expander("📞 联系我们", expanded=False):
    st.write("**总部地址：** 北京市海淀区中关村科技园区")
    st.write("**联系电话：** 400-123-4567")
    st.write("**官方网站：** www.example.com")
    st.write("**邮箱：** info@example.com")