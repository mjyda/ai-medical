from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import Tool
from app.config.config import API_CONFIG, SYSTEM_CONFIG
from app.backend.services.appointment_service import AppointmentService
from app.rag.rag_service import RAGService
from app.backend.services.chat_memory_service import ChatMemoryService
import datetime

class XiaozhiAgent:
    def __init__(self):
        self.llm = self._init_llm()
        self.appointment_service = AppointmentService()
        self.rag_service = RAGService()
        self.chat_memory_service = ChatMemoryService()
        self.tools = self._init_tools()
    
    def _init_llm(self):
        """初始化大模型"""
        return ChatOpenAI(
            api_key=API_CONFIG['local_model']['api_key'],
            model=API_CONFIG['local_model']['model_name'],
            base_url=API_CONFIG['local_model']['base_url'],
            temperature=SYSTEM_CONFIG['chat']['temperature']
        )
    
    def _init_tools(self):
        """初始化工具"""
        tools = [
            Tool(
                name="book_appointment",
                func=self.book_appointment,
                description="预约挂号：根据用户提供的信息预约挂号，需要参数：username（患者姓名）、id_card（身份证号）、department（预约科室）、date（预约日期）、time（预约时间）、doctor_name（医生姓名，可选）"
            ),
            Tool(
                name="cancel_appointment",
                func=self.cancel_appointment,
                description="取消预约：根据用户提供的信息取消预约，需要参数：username（患者姓名）、id_card（身份证号）、department（预约科室）、date（预约日期）、time（预约时间）"
            ),
            Tool(
                name="query_department",
                func=self.query_department,
                description="查询号源：查询指定科室、日期、时间是否有号源，需要参数：department（科室名称）、date（日期）、time（时间）、doctor_name（医生姓名，可选）"
            ),
            Tool(
                name="retrieve_knowledge",
                func=self.retrieve_knowledge,
                description="检索知识库：根据用户问题检索相关的医疗知识"
            )
        ]
        return tools
    
    def book_appointment(self, **kwargs):
        """预约挂号"""
        success, message = self.appointment_service.save_appointment(kwargs)
        return message
    
    def cancel_appointment(self, **kwargs):
        """取消预约"""
        success, message = self.appointment_service.cancel_appointment(kwargs)
        return message
    
    def query_department(self, department, date, time, doctor_name=None):
        """查询号源"""
        has_availability = self.appointment_service.query_department(department, date, time, doctor_name)
        if has_availability:
            return f"{department}在{date} {time}有号源"
        else:
            return f"{department}在{date} {time}没有号源"
    
    def retrieve_knowledge(self, query):
        """检索知识库"""
        context = self.rag_service.get_context(query)
        return context if context else "未找到相关信息"
    
    def get_system_prompt(self):
        """获取系统提示词"""
        with open('app/config/prompt_template.txt', 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        prompt = prompt_template.format(current_date=current_date)
        return prompt
    
    def chat(self, memory_id, user_message):
        """处理对话"""
        # 获取对话历史
        history = self.chat_memory_service.get_messages(memory_id)
        
        # 检索知识库，获取相关上下文
        knowledge_context = self.rag_service.get_context(user_message)
        
        # 构建系统提示词，包含知识库上下文
        system_prompt = self.get_system_prompt()
        if knowledge_context:
            system_prompt += f"\n\n## 知识库信息\n以下是关于用户问题的相关知识库信息，如果有用的话请参考：\n{knowledge_context}"
        
        # 构建消息列表
        messages = [
            SystemMessage(content=system_prompt)
        ]
        
        # 添加历史消息
        for msg in history:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            else:
                messages.append(AIMessage(content=msg['content']))
        
        # 添加当前用户消息
        messages.append(HumanMessage(content=user_message))
        
        # 调用大模型
        response = self.llm.invoke(messages)
        
        # 保存对话历史
        self.chat_memory_service.add_message(memory_id, {"role": "user", "content": user_message})
        self.chat_memory_service.add_message(memory_id, {"role": "assistant", "content": response.content})
        
        return response.content
    
    def stream_chat(self, memory_id, user_message):
        """流式处理对话"""
        # 获取对话历史
        history = self.chat_memory_service.get_messages(memory_id)
        
        # 检索知识库，获取相关上下文
        knowledge_context = self.rag_service.get_context(user_message)
        
        # 构建系统提示词，包含知识库上下文
        system_prompt = self.get_system_prompt()
        if knowledge_context:
            system_prompt += f"\n\n## 知识库信息\n以下是关于用户问题的相关知识库信息，如果有用的话请参考：\n{knowledge_context}"
        
        # 构建消息列表
        messages = [
            SystemMessage(content=system_prompt)
        ]
        
        # 添加历史消息
        for msg in history:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            else:
                messages.append(AIMessage(content=msg['content']))
        
        # 添加当前用户消息
        messages.append(HumanMessage(content=user_message))
        
        # 调用大模型，获取流式响应
        full_response = ""
        for chunk in self.llm.stream(messages):
            if hasattr(chunk, 'content') and chunk.content:
                full_response += chunk.content
                yield chunk.content
        
        # 保存对话历史
        self.chat_memory_service.add_message(memory_id, {"role": "user", "content": user_message})
        self.chat_memory_service.add_message(memory_id, {"role": "assistant", "content": full_response})
    
    def get_all_sessions(self):
        """获取所有会话历史"""
        return self.chat_memory_service.get_all_sessions()
    
    def load_session(self, memory_id):
        """加载指定会话的历史消息"""
        return self.chat_memory_service.get_messages(memory_id)
    
    def delete_session(self, memory_id):
        """删除指定会话的聊天历史"""
        self.chat_memory_service.delete_messages(memory_id)
