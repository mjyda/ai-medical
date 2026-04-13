from app.database.mongodb_connection import MongoDBConnection
import json

class ChatMemoryService:
    def __init__(self):
        self.collection_name = "chat_messages"
    
    def get_messages(self, memory_id):
        """获取对话历史"""
        with MongoDBConnection() as conn:
            collection = conn.get_collection(self.collection_name)
            chat = collection.find_one({"memory_id": memory_id})
            if chat:
                return json.loads(chat['content'])
            return []
    
    def update_messages(self, memory_id, messages):
        """更新对话历史"""
        with MongoDBConnection() as conn:
            collection = conn.get_collection(self.collection_name)
            content = json.dumps(messages, ensure_ascii=False)
            collection.update_one(
                {"memory_id": memory_id},
                {"$set": {"content": content}},
                upsert=True
            )
    
    def delete_messages(self, memory_id):
        """删除对话历史"""
        with MongoDBConnection() as conn:
            collection = conn.get_collection(self.collection_name)
            collection.delete_one({"memory_id": memory_id})
    
    def add_message(self, memory_id, message):
        """添加一条消息"""
        messages = self.get_messages(memory_id)
        messages.append(message)
        # 限制历史消息数量
        if len(messages) > 20:
            messages = messages[-20:]
        self.update_messages(memory_id, messages)
    
    def get_all_sessions(self):
        """获取所有会话列表"""
        with MongoDBConnection() as conn:
            collection = conn.get_collection(self.collection_name)
            sessions = []
            for chat in collection.find():
                memory_id = chat['memory_id']
                messages = json.loads(chat['content'])
                if messages:
                    # 获取会话的第一条消息作为标题
                    first_message = messages[0]['content'][:50] + '...' if len(messages[0]['content']) > 50 else messages[0]['content']
                    # 获取会话的最后一条消息的时间
                    last_message_time = chat.get('last_updated', '未知时间')
                    sessions.append({
                        'memory_id': memory_id,
                        'title': first_message,
                        'last_updated': last_message_time,
                        'message_count': len(messages)
                    })
            # 按最后更新时间排序
            sessions.sort(key=lambda x: x['last_updated'], reverse=True)
            return sessions
