from src.services.course_fetcher import CourseFetcher
from src.services.ai_ranker import AIRanker
from src.services.lesson_mapper import LessonMapper


class CourseController:
    def __init__(self, db, ai=None):
        self.db = db
        self.course_fetcher = CourseFetcher()
        self.ai_ranker = AIRanker()
        self.lesson_mapper = LessonMapper()
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
        if not name or not name.strip():
            raise ValueError("Tên khóa học không được để trống")

        try:
            # 1. lưu course
            course_id = self.db.add_course(
                user_id,
                name.strip(),
                code.strip() if code else "",
                professor.strip() if professor else ""
            )

            # 2. search internet
            results = self.fetcher.search_courses(name)

            # 3. AI lọc
            ranked = self.ranker.rank(results)

            # 4. convert → lesson
            lessons = self.mapper.map_to_lessons(ranked)

            # 5. lưu lesson
            for l in lessons:
                self.db.add_lesson(
                    course_id,
                    l["title"],
                    l["duration"],
                    l["type"],
                    l["url"],
                    l["has_exercise"]
                )

            return True

        except Exception as e:
            print("❌ Lỗi thêm course:", e)
            return False

    # ================= DELETE =================
    def delete_course(self, course_id):
        try:
            query = "DELETE FROM courses WHERE id=?"
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
            SET name=?, code=?, professor=?
            WHERE id=?
            """
            return self.db.execute(
                query,
                (name.strip(), code.strip(), professor.strip(), course_id)
            )
        except Exception as e:
            print("❌ Lỗi update course:", e)
            return False