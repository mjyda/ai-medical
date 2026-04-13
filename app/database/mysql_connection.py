from app.database.connection_pool import mysql_pool

class MySQLConnection:
    def __init__(self):
        self.connection = mysql_pool.get_connection()
        self.cursor = None
        if self.connection:
            self.cursor = self.connection.cursor(dictionary=True)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def execute(self, query, params=None):
        if self.cursor:
            self.cursor.execute(query, params or ())
            return self.cursor
        return None
    
    def commit(self):
        if self.connection:
            self.connection.commit()
    
    def fetch_all(self):
        if self.cursor:
            return self.cursor.fetchall()
        return []
    
    def fetch_one(self):
        if self.cursor:
            return self.cursor.fetchone()
        return None
    
    def get_connection(self):
        return self.connection
