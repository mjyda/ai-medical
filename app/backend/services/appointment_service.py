from app.database.mysql_connection import MySQLConnection

class AppointmentService:
    def __init__(self):
        pass
    
    def save_appointment(self, appointment_data):
        """保存预约信息"""
        with MySQLConnection() as conn:
            if not conn.cursor:
                return False, "数据库连接失败"
            # 检查是否已有相同的预约
            query = """
                SELECT * FROM appointment 
                WHERE patient_name = %s AND patient_id = %s AND department_id = %s AND appointment_date = %s AND appointment_time = %s
            """
            conn.execute(query, (
                appointment_data['patient_name'],
                appointment_data['patient_id'],
                appointment_data['department_id'],
                appointment_data['appointment_date'],
                appointment_data['appointment_time']
            ))
            existing = conn.fetch_one()
            
            if existing:
                return False, "您在相同的科室和时间已有预约"
            
            # 插入新预约
            insert_query = """
                INSERT INTO appointment (patient_name, patient_id, department_id, doctor_id, appointment_date, appointment_time) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            conn.execute(insert_query, (
                appointment_data['patient_name'],
                appointment_data['patient_id'],
                appointment_data['department_id'],
                appointment_data.get('doctor_id'),
                appointment_data['appointment_date'],
                appointment_data['appointment_time']
            ))
            conn.commit()
            return True, "预约成功"
    
    def cancel_appointment(self, appointment_data):
        """取消预约"""
        with MySQLConnection() as conn:
            if not conn.cursor:
                return False, "数据库连接失败"
            # 查找预约
            query = """
                SELECT id FROM appointment 
                WHERE patient_name = %s AND patient_id = %s AND department_id = %s AND appointment_date = %s AND appointment_time = %s
            """
            conn.execute(query, (
                appointment_data['patient_name'],
                appointment_data['patient_id'],
                appointment_data['department_id'],
                appointment_data['appointment_date'],
                appointment_data['appointment_time']
            ))
            appointment = conn.fetch_one()
            
            if not appointment:
                return False, "您没有预约记录，请核对预约信息"
            
            # 删除预约
            delete_query = "DELETE FROM appointment WHERE id = %s"
            conn.execute(delete_query, (appointment['id'],))
            conn.commit()
            return True, "取消预约成功"
    
    def query_department(self, department, date, time, doctor_name=None):
        """查询是否有号源"""
        # 这里可以根据实际情况实现号源查询逻辑
        # 目前返回默认有号
        return True
