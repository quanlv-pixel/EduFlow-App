import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime

class Database:
    def __init__(self):
        load_dotenv()
        try:
            # 1. Kết nối ban đầu (không chỉ định DB để tạo mới nếu cần)
            self.conn = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "123456")
            )
            self.cursor = self.conn.cursor()
            
            # 2. Tạo và sử dụng database education
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS education")
            self.cursor.execute("USE education")
            
            # 3. Khởi tạo toàn bộ cấu trúc bảng
            self.init_db_structure()
            print("✅ Hệ thống Cơ sở dữ liệu EduFlow đã sẵn sàng!")
            
        except mysql.connector.Error as err:
            print(f"❌ Lỗi kết nối Database: {err}")

    def init_db_structure(self):
        """Chạy script tạo bảng theo đúng Schema Quân đã gửi"""
        queries = [
            # Bảng Users
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Bảng Courses
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                code VARCHAR(50),
                professor VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            # Bảng Schedule
            """
            CREATE TABLE IF NOT EXISTS schedule (
                id INT AUTO_INCREMENT PRIMARY KEY,
                course_id INT NOT NULL,
                day_of_week INT NOT NULL,
                start_time TIME,
                end_time TIME,
                room VARCHAR(50),
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
            """,
            # Bảng Progress
            """
            CREATE TABLE IF NOT EXISTS progress (
                id INT AUTO_INCREMENT PRIMARY KEY,
                course_id INT NOT NULL UNIQUE,
                percent INT DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
            """,
            # Bảng Documents (Input cho AI)
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                filename VARCHAR(255),
                content LONGTEXT,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            # Bảng Summaries (Output từ AI)
            """
            CREATE TABLE IF NOT EXISTS summaries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                document_id INT NOT NULL,
                summary_text TEXT,
                type VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            )
            """
        ]
        
        for q in queries:
            self.cursor.execute(q)
        
        # Thêm các Index để truy vấn nhanh hơn
        try:
            self.cursor.execute("CREATE INDEX idx_courses_user ON courses(user_id)")
            self.cursor.execute("CREATE INDEX idx_documents_user ON documents(user_id)")
            self.cursor.execute("CREATE INDEX idx_summaries_doc ON summaries(document_id)")
        except:
            pass # Nếu index tồn tại rồi thì bỏ qua
            
        self.conn.commit()

    def save_document_and_summary(self, user_id, filename, content, summary, summary_type="detailed"):
        """Hàm tiện ích: Lưu cả file gốc và bản tóm tắt vào DB"""
        try:
            # 1. Lưu document
            doc_query = "INSERT INTO documents (user_id, filename, content) VALUES (%s, %s, %s)"
            self.cursor.execute(doc_query, (user_id, filename, content))
            doc_id = self.cursor.lastrowid
            
            # 2. Lưu summary
            sum_query = "INSERT INTO summaries (document_id, summary_text, type) VALUES (%s, %s, %s)"
            self.cursor.execute(sum_query, (doc_id, summary, summary_type))
            
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"❌ Lỗi khi lưu dữ liệu: {err}")
            return False

    def __del__(self):
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()