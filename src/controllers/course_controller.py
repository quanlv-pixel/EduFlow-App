class CourseController:
    def __init__(self, db, ai=None):
        self.db = db
        self.ai = ai  # optional (sau này dùng AI gợi ý khóa học)

    # ================= GET =================
    def get_courses(self, user_id):
        try:
            courses = self.db.get_courses(user_id)
            return courses or []
        except Exception as e:
            print("❌ Lỗi lấy courses:", e)
            return []

    # ================= ADD =================
    def add_course(self, user_id, name, code, professor):
        # validate
        if not name or not name.strip():
            raise ValueError("Tên khóa học không được để trống")

        try:
            return self.db.add_course(
                user_id,
                name.strip(),
                code.strip() if code else "",
                professor.strip() if professor else ""
            )
        except Exception as e:
            print("❌ Lỗi thêm course:", e)
            return False

    # ================= DELETE =================
    def delete_course(self, course_id):
        try:
            query = "DELETE FROM courses WHERE id=%s"
            return self.db.execute(query, (course_id,))
        except Exception as e:
            print("❌ Lỗi xóa course:", e)
            return False

    # ================= UPDATE =================
    def update_course(self, course_id, name, code, professor):
        if not name or not name.strip():
            raise ValueError("Tên khóa học không hợp lệ")

        try:
            query = """
            UPDATE courses 
            SET name=%s, code=%s, professor=%s
            WHERE id=%s
            """
            return self.db.execute(
                query,
                (name.strip(), code.strip(), professor.strip(), course_id)
            )
        except Exception as e:
            print("❌ Lỗi update course:", e)
            return False