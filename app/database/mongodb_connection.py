from app.database.connection_pool import mongodb_db

class MongoDBConnection:
    def __init__(self):
        self.db = mongodb_db
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # 全局客户端不需要在这里关闭
    
    def get_db(self):
        return self.db
    
    def get_collection(self, collection_name):
        if self.db is not None:
            return self.db[collection_name]
        return None
    
    def insert_one(self, collection_name, document):
        collection = self.get_collection(collection_name)
        if collection is not None:
            return collection.insert_one(document)
        return None
    
    def find_one(self, collection_name, query):
        collection = self.get_collection(collection_name)
        if collection is not None:
            return collection.find_one(query)
        return None
    
    def update_one(self, collection_name, query, update):
        collection = self.get_collection(collection_name)
        if collection is not None:
            return collection.update_one(query, update)
        return None
    
    def delete_one(self, collection_name, query):
        collection = self.get_collection(collection_name)
        if collection is not None:
            return collection.delete_one(query)
        return None
