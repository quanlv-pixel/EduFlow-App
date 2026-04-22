import mysql.connector
import os
from dotenv import load_dotenv


class Database:
    def __init__(self):
        load_dotenv()

        self.config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD"),
        }

        if not self.config["password"]:
            raise ValueError("❌ Thiếu DB_PASSWORD trong .env")

        try:
            # ===== CONNECT =====
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor()

            # ===== CREATE DB =====
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS education")
            self.cursor.execute("USE education")

            # ===== INIT TABLE =====
            self.init_db_structure()

            print("✅ Database EduFlow ready!")

        except mysql.connector.Error as err:
            print(f"❌ Lỗi DB: {err}")

    # ================= INIT =================
    def init_db_structure(self):
        queries = [

            # USERS
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # COURSES
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                code VARCHAR(50),
                professor VARCHAR(100),
                progress INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,

            # SCHEDULE (đổi sang user_id cho dễ dùng UI)
            """
            CREATE TABLE IF NOT EXISTS schedule (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                course VARCHAR(255),
                room VARCHAR(50),
                day INT,
                slot INT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
            """,

            # DOCUMENTS
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                filename VARCHAR(255),
                content LONGTEXT,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,

            # SUMMARIES
            """
            CREATE TABLE IF NOT EXISTS summaries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                document_id INT,
                summary_text TEXT,
                type VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            )
            """,

            # FLASHCARDS
            """
            CREATE TABLE IF NOT EXISTS flashcards (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                question TEXT,
                answer TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        ]

        for q in queries:
            self.cursor.execute(q)

        # ===== INDEX (an toàn) =====
        indexes = [
            "CREATE INDEX idx_courses_user ON courses(user_id)",
            "CREATE INDEX idx_schedule_user ON schedule(user_id)",
            "CREATE INDEX idx_docs_user ON documents(user_id)",
            "CREATE INDEX idx_flash_user ON flashcards(user_id)"
        ]

        for idx in indexes:
            try:
                self.cursor.execute(idx)
            except:
                pass

        self.conn.commit()

    # ================= CORE QUERY =================
    def execute(self, query, params=None, fetch=False):
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(query, params or ())

            if fetch:
                data = cursor.fetchall()
                cursor.close()
                return data

            self.conn.commit()
            cursor.close()
            return True

        except mysql.connector.Error as err:
            print(f"❌ Query lỗi: {err}")
            return None

    # ================= AUTH =================
    def get_user(self, email, password):
        query = """
        SELECT id, name, email 
        FROM users 
        WHERE email=%s AND password=%s
        """
        result = self.execute(query, (email, password), fetch=True)
        return result[0] if result else None

    # ================= COURSES =================
    def get_courses(self, user_id):
        query = """
        SELECT id, name, code, professor, progress
        FROM courses
        WHERE user_id=%s
        """
        return self.execute(query, (user_id,), fetch=True)

    def add_course(self, user_id, name, code, professor):
        query = """
        INSERT INTO courses (user_id, name, code, professor)
        VALUES (%s, %s, %s, %s)
        """
        return self.execute(query, (user_id, name, code, professor))

    # ================= SCHEDULE =================
    def get_schedule(self, user_id):
        query = """
        SELECT course, room, day, slot
        FROM schedule
        WHERE user_id=%s
        """
        return self.execute(query, (user_id,), fetch=True)

    def add_schedule(self, user_id, course, room, day, slot):
        query = """
        INSERT INTO schedule (user_id, course, room, day, slot)
        VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute(query, (user_id, course, room, day, slot))

    # ================= FLASHCARDS =================
    def get_flashcards(self, user_id):
        query = """
        SELECT question, answer
        FROM flashcards
        WHERE user_id=%s
        ORDER BY id DESC
        """
        return self.execute(query, (user_id,), fetch=True)

    def add_flashcard(self, user_id, question, answer):
        query = """
        INSERT INTO flashcards (user_id, question, answer)
        VALUES (%s, %s, %s)
        """
        return self.execute(query, (user_id, question, answer))

    # ================= SUMMARY =================
    def save_document_and_summary(self, user_id, filename, content, summary):
        try:
            cursor = self.conn.cursor()

            cursor.execute(
                "INSERT INTO documents (user_id, filename, content) VALUES (%s, %s, %s)",
                (user_id, filename, content)
            )
            doc_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO summaries (document_id, summary_text, type) VALUES (%s, %s, %s)",
                (doc_id, summary, "ai")
            )

            self.conn.commit()
            cursor.close()
            return True

        except mysql.connector.Error as err:
            print(f"❌ Lỗi lưu DB: {err}")
            return False

    # ================= CLOSE =================
    def close(self):
        if self.conn.is_connected():
            self.conn.close()