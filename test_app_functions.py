import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.backend.services.appointment_service import AppointmentService
from app.backend.services.chat_memory_service import ChatMemoryService
from app.backend.agents.xiaozhi_agent import XiaozhiAgent

def test_appointment_service():
    print("测试预约服务...")
    try:
        service = AppointmentService()
        
        # 测试保存预约
        appointment_data = {
            'patient_name': '张三',
            'patient_id': '123456789',
            'department_id': 1,
            'doctor_id': None,
            'appointment_date': '2026-04-09',
            'appointment_time': '09:00'
        }
        success, message = service.save_appointment(appointment_data)
        print(f"预约保存结果: {success}, {message}")
        
        return True
    except Exception as e:
        print(f"预约服务测试失败: {e}")
        return False

def test_chat_memory_service():
    print("\n测试对话记忆服务...")
    try:
        service = ChatMemoryService()
        
        # 测试添加消息
        memory_id = "test_session_001"
        service.add_message(memory_id, {"role": "user", "content": "你好，我想咨询一下神经内科"})
        service.add_message(memory_id, {"role": "assistant", "content": "您好，我是硅谷小智，很高兴为您服务。神经内科主要负责神经系统疾病的诊断和治疗，请问您有什么具体问题？"})
        
        # 测试获取消息
        messages = service.get_messages(memory_id)
        print(f"获取到 {len(messages)} 条对话消息")
        for msg in messages:
            print(f"  {msg['role']}: {msg['content'][:50]}...")
        
        return True
    except Exception as e:
        print(f"对话记忆服务测试失败: {e}")
        return False

def test_agent():
    print("\n测试AI代理...")
    try:
        agent = XiaozhiAgent()
        
        # 测试简单对话
        session_id = "test_session_004"
        response = agent.chat(session_id, "你好")
        try:
            print(f"AI回复: {response[:100]}...")
        except UnicodeEncodeError:
            print("AI回复: [包含特殊字符，无法在控制台显示]")
        
        return True
    except Exception as e:
        print(f"AI代理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试应用功能...")
    
    appointment_ok = test_appointment_service()
    memory_ok = test_chat_memory_service()
    agent_ok = test_agent()
    
    print("\n测试结果:")
    print(f"预约服务: {'成功' if appointment_ok else '失败'}")
    print(f"对话记忆: {'成功' if memory_ok else '失败'}")
    print(f"AI代理: {'成功' if agent_ok else '失败'}")
