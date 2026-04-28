import sqlite3
import os


class Database:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "../../eduflow.db")
        db_path = os.path.abspath(db_path)

        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

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
                name TEXT,
                email TEXT UNIQUE,
                password TEXT
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

            # 🔥 LESSONS (NEW)
            """
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER,
                title TEXT,
                url TEXT,
                source TEXT
            )
            """,

            # 🔥 RESOURCES (NEW)
            """
            CREATE TABLE IF NOT EXISTS course_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER,
                title TEXT,
                url TEXT
            )
            """,

            # SCHEDULE
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
            """,

            # MIGRATIONS
            """
            CREATE TABLE IF NOT EXISTS migrations (
                id TEXT PRIMARY KEY
            )
            """
        ]

        for q in queries:
            self.cursor.execute(q)

        self.conn.commit()
        self.migrate_once()
        self.create_default_user()

    # ================= MIGRATION =================
    def migrate_once(self):
        mid = "schedule_time_to_minutes"

        row = self.cursor.execute(
            "SELECT id FROM migrations WHERE id=?", (mid,)
        ).fetchone()

        if not row:
            self.cursor.execute(
                "UPDATE schedule SET start_time = start_time * 60, end_time = end_time * 60"
            )
            self.cursor.execute(
                "INSERT INTO migrations (id) VALUES (?)", (mid,)
            )
            self.conn.commit()

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
                return [dict(r) for r in cur.fetchall()]

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
            True
        )

    def add_course(self, user_id, name, code, professor):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO courses (user_id, name, code, professor) VALUES (?, ?, ?, ?)",
            (user_id, name, code, professor)
        )
        self.conn.commit()
        return cur.lastrowid  # 🔥 IMPORTANT

    # ================= LESSON =================
    def add_lesson(self, course_id, title, url, source):
        return self.execute(
            "INSERT INTO lessons (course_id, title, url, source) VALUES (?, ?, ?, ?)",
            (course_id, title, url, source)
        )

    def get_lessons(self, course_id):
        return self.execute(
            "SELECT * FROM lessons WHERE course_id=?",
            (course_id,),
            True
        )

    # ================= RESOURCE =================
    def add_resource(self, course_id, title, url):
        return self.execute(
            "INSERT INTO course_resources (course_id, title, url) VALUES (?, ?, ?)",
            (course_id, title, url)
        )

    def get_resources(self, course_id):
        return self.execute(
            "SELECT * FROM course_resources WHERE course_id=?",
            (course_id,),
            True
        )

    # ================= SCHEDULE =================
    def get_schedule(self, user_id):
        return self.execute(
            "SELECT * FROM schedule WHERE user_id=?",
            (user_id,),
            True
        )

    def add_schedule(self, user_id, course, room, day, start, end):
        return self.execute(
            """
            INSERT INTO schedule (user_id, course, room, day, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, course, room, day, start, end)
        )

    def delete_schedule(self, schedule_id):
        return self.execute(
            "DELETE FROM schedule WHERE id=?",
            (schedule_id,)
        )

    # ================= FLASHCARDS =================
    def get_flashcards(self, user_id):
        return self.execute(
            "SELECT * FROM flashcards WHERE user_id=?",
            (user_id,),
            True
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