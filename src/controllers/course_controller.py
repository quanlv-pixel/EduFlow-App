from src.services.course_fetcher import CourseFetcher
from src.services.ai_ranker import AIRanker
from src.services.lesson_mapper import LessonMapper


class CourseController:
    # FIX: Đổi tên attribute cho nhất quán: fetcher / ranker / mapper
    def __init__(self, db, ai=None):
        self.db = db
        self.ai = ai

        # FIX: Phiên bản cũ dùng self.course_fetcher, self.ai_ranker, self.lesson_mapper
        # nhưng bên dưới lại gọi self.fetcher, self.ranker, self.mapper → NameError
        # Sửa thống nhất thành tên ngắn
        self.fetcher = CourseFetcher()
        self.ranker = AIRanker()
        self.mapper = LessonMapper()

    # ================= GET =================
    def get_courses(self, user_id):
        try:
            courses = self.db.get_courses(user_id)
            if not courses:
                return []

            # Gắn thêm progress thực tế từ DB vào mỗi course
            for c in courses:
                c["progress"] = self.db.get_course_progress(c["id"])

            return courses
        except Exception as e:
            print("❌ Lỗi lấy courses:", e)
            return []

    def get_lessons(self, course_id):
        try:
            return self.db.get_lessons(course_id) or []
        except Exception as e:
            print("❌ Lỗi lấy lessons:", e)
            return []

    # ================= SEARCH (BƯỚC 1 KHI ADD COURSE) =================
    # FIX: Tách riêng search ra khỏi add_course
    # UI sẽ gọi hàm này trước để lấy danh sách course gợi ý
    def search_online_courses(self, query: str) -> list:
        """
        Tìm kiếm course online theo từ khóa.
        Trả về list đã được rank bởi AIRanker.
        UI dùng kết quả này để cho user chọn.
        """
        try:
            results = self.fetcher.search_courses(query)
            ranked = self.ranker.rank(results)
            return ranked
        except Exception as e:
            print("❌ Lỗi search online courses:", e)
            return []

    # ================= ADD COURSE (BƯỚC 2 KHI ADD COURSE) =================
    # FIX: add_course CHỈ lưu course vào DB, không tự động tạo lesson
    def add_course(self, user_id, name, code, professor) -> int | None:
        """
        Lưu course vào DB.
        Trả về course_id để dùng cho generate_lessons_from_course().
        """
        if not name or not name.strip():
            raise ValueError("Tên khóa học không được để trống")

        try:
            course_id = self.db.add_course(
                user_id,
                name.strip(),
                code.strip() if code else "",
                professor.strip() if professor else ""
            )
            return course_id
        except Exception as e:
            print("❌ Lỗi thêm course:", e)
            return None

    # ================= GENERATE LESSONS (BƯỚC 3 KHI ADD COURSE) =================
    # FIX: Chỉ được gọi sau khi user đã chọn 1 course từ danh sách search
    def generate_lessons_from_course(self, course_id: int, selected_course: dict) -> list:
        """
        Nhận course_id đã lưu trong DB và dict của course user chọn.
        Dùng LessonMapper để chia thành các bài giảng rồi lưu vào DB.
        Trả về list lessons đã tạo.
        """
        try:
            lessons = self.mapper.split_course(selected_course)

            for l in lessons:
                # FIX: Gọi đúng signature của db.add_lesson()
                self.db.add_lesson(
                    course_id,
                    l.get("title"),
                    l.get("url"),
                    l.get("source"),
                    l.get("duration"),      # dùng .get()
                    l.get("type"),
                    l.get("has_exercise"),
                    completed=False,
                    topic_key=l.get("topic_key"),
                    course_title=l.get("course_title"),
                    minutes=l.get("minutes")
                )

            return lessons
        except Exception as e:
            print("❌ Lỗi generate lessons:", e)
            return []

    # ================= PROGRESS =================
    def mark_lesson_done(self, lesson_id: int, done: bool = True):
        """Đánh dấu lesson hoàn thành hoặc chưa hoàn thành."""
        try:
            return self.db.set_lesson_completed(lesson_id, done)
        except Exception as e:
            print("❌ Lỗi mark lesson:", e)
            return False

    def get_progress(self, course_id: int) -> int:
        """Tính % hoàn thành của course (0–100)."""
        try:
            return self.db.get_course_progress(course_id)
        except Exception as e:
            print("❌ Lỗi tính progress:", e)
            return 0

    # ================= DELETE =================
    def delete_course(self, course_id: int):
        try:
            return self.db.delete_course(course_id)
        except Exception as e:
            print("❌ Lỗi xóa course:", e)
            return False

    # ================= UPDATE =================
    def update_course(self, course_id, name, code, professor):
        if not name or not name.strip():
            raise ValueError("Tên khóa học không hợp lệ")

        try:
            return self.db.update_course(
                course_id,
                name.strip(),
                code.strip() if code else "",
                professor.strip() if professor else ""
            )
        except Exception as e:
            print("❌ Lỗi update course:", e)
            return False

    # ================= FLASHCARD (tùy chọn, nếu có AI) =================
    def generate_flashcard_for_lesson(self, lesson: dict) -> list:
        if not self.ai:
            return []
        try:
            topic = lesson.get("title", "")
            course_title = lesson.get("course_title", "")

            # Tạo prompt kết hợp tên bài + tên khóa học
            prompt = f"Tạo flashcard về bài: {topic}"
            if course_title:
                prompt += f" (thuộc khóa học: {course_title})"

            # Dùng đúng method có trong AIEngine
            cards = self.ai.generate_flashcards_from_topic(prompt)
            return cards
        except Exception as e:
            print("❌ Lỗi tạo flashcard:", e)
            return []