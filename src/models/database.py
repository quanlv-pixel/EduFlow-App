import sqlite3
import os


class Database:
    def __init__(self):
        # 📁 path DB (ổn định mọi máy)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "../../eduflow.db")
        db_path = os.path.abspath(db_path)

        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        # bật foreign key
        self.cursor.execute("PRAGMA foreign_keys = ON")

        self.init_db()
        print("✅ SQLite EduFlow ready!")

    # ================= INIT =================
    def init_db(self):
        queries = [

            # USERS
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
            """,

            # COURSES
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                code TEXT,
                professor TEXT
            )
            """,

            # ✅ SCHEDULE (NEW VERSION)
            """
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                course TEXT,
                room TEXT,
                day INTEGER,
                start_time INTEGER,
                end_time INTEGER
            )
            """,

            # FLASHCARDS
            """
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question TEXT,
                answer TEXT
            )
            """,

            # DOCUMENTS
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                filename TEXT,
                content TEXT
            )
            """,

            # SUMMARIES
            """
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                summary_text TEXT
            )
            """
        ]

        for q in queries:
            self.cursor.execute(q)

        self.conn.commit()

        self.create_default_user()

    # ================= DEFAULT USER =================
    def create_default_user(self):
        self.cursor.execute(
            "SELECT * FROM users WHERE email=?",
            ("admin@eduflow.com",)
        )

        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                ("ADMIN", "admin@eduflow.com", "123")
            )
            self.conn.commit()

    # ================= CORE =================
    def execute(self, query, params=(), fetch=False):
        try:
            cur = self.conn.cursor()
            cur.execute(query, params)

            if fetch:
                rows = cur.fetchall()
                return [dict(r) for r in rows]

            self.conn.commit()
            return True

        except Exception as e:
            print("❌ DB ERROR:", e)
            return None

    # ================= AUTH =================
    def get_user(self, email, password):
        result = self.execute(
            "SELECT id, name, email FROM users WHERE email=? AND password=?",
            (email, password),
            fetch=True
        )
        return result[0] if result else None

    # ================= COURSES =================
    def get_courses(self, user_id):
        return self.execute(
            "SELECT * FROM courses WHERE user_id=?",
            (user_id,),
            fetch=True
        )

    def add_course(self, user_id, name, code, professor):
        return self.execute(
            "INSERT INTO courses (user_id, name, code, professor) VALUES (?, ?, ?, ?)",
            (user_id, name, code, professor)
        )

    # ================= SCHEDULE =================
    def get_schedule(self, user_id):
        return self.execute(
            "SELECT * FROM schedule WHERE user_id=?",
            (user_id,),
            fetch=True
        )

    def add_schedule(self, user_id, course, room, day, start, end):
        return self.execute(
            """
            INSERT INTO schedule (user_id, course, room, day, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, course, room, day, start, end)
        )

    # ================= FLASHCARDS =================
    def get_flashcards(self, user_id):
        return self.execute(
            "SELECT * FROM flashcards WHERE user_id=?",
            (user_id,),
            fetch=True
        )

    def add_flashcard(self, user_id, q, a):
        return self.execute(
            "INSERT INTO flashcards (user_id, question, answer) VALUES (?, ?, ?)",
            (user_id, q, a)
        )

    # ================= SUMMARY =================
    def save_document_and_summary(self, user_id, filename, content, summary):
        try:
            cur = self.conn.cursor()

            cur.execute(
                "INSERT INTO documents (user_id, filename, content) VALUES (?, ?, ?)",
                (user_id, filename, content)
            )
            doc_id = cur.lastrowid

            cur.execute(
                "INSERT INTO summaries (document_id, summary_text) VALUES (?, ?)",
                (doc_id, summary)
            )

            self.conn.commit()
            return True

        except Exception as e:
            print("❌ SAVE ERROR:", e)
            return False

    # ================= CLOSE =================
    def close(self):
        self.conn.close()