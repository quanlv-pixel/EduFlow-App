import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime

class Database:
    def __init__(self):
        load_dotenv()
        try:
            # 1. Kết nối ban đầu để kiểm tra/tạo Database
            self.conn = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
            self.cursor = self.conn.cursor()
            
            # 2. Tạo Database nếu chưa có
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}")
            self.conn.database = os.getenv('DB_NAME')
            
            self.create_table()
            print("✅ Kết nối MySQL thành công!")
        except mysql.connector.Error as err:
            print(f"❌ Lỗi kết nối MySQL: {err}")

    def create_table(self):
        """Tạo bảng lưu lịch sử tóm tắt"""
        query = """
        CREATE TABLE IF NOT EXISTS history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255),
            original_text LONGTEXT,
            summary_text TEXT,
            created_at DATETIME
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    def save_summary(self, filename, original, summary):
        """Lưu kết quả vào MySQL"""
        query = "INSERT INTO history (filename, original_text, summary_text, created_at) VALUES (%s, %s, %s, %s)"
        now = datetime.now()
        values = (filename, original, summary, now)
        
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            print("✅ Đã lưu lịch sử vào MySQL")
        except mysql.connector.Error as err:
            print(f"❌ Lỗi lưu dữ liệu: {err}")

    def __del__(self):
        """Đóng kết nối khi app tắt"""
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

if __name__ == "__main__":
    db = Database()