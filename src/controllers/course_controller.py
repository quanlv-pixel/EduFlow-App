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
            url = lesson.get("url", "")
            source = lesson.get("source", "")

            # Kiểm tra nếu bài học là video YouTube (dựa vào source hoặc URL)
            if source == "YouTube" or (url and ("youtube.com" in url.lower() or "youtu.be" in url.lower())):
                print(f"🎬 Phát hiện bài học YouTube: {topic}. Đang cào phụ đề và tạo trắc nghiệm...")
                # Gọi hàm xử lý trắc nghiệm từ YouTube mới cấu trúc lại
                return self.ai.generate_flashcards_from_youtube(url, topic)
            
            else:
                # Luồng cũ: Tạo prompt kết hợp tên bài + tên khóa học cho tài liệu thông thường
                print(f"📚 Bài học dạng tài liệu/topic: {topic}. Đang tạo flashcard thường...")
                prompt = f"Tạo flashcard về bài: {topic}"
                if course_title:
                    prompt += f" (thuộc khóa học: {course_title})"

                return self.ai.generate_flashcards_from_topic(prompt)

        except Exception as e:
            print("❌ Lỗi khi tạo flashcard từ AI tại Controller:", e)
            return []
        

    def get_course_tutorial(self, source_platform: str, course_title: str) -> str:
            """AI tạo cẩm nang hướng dẫn học tối ưu cho riêng từng nền tảng Web"""
            if not self.ai:
                return "Chào mừng bạn đến với khóa học. Hãy truy cập liên kết chính thức để tự học theo lộ trình chuẩn của website."
                
            prompt = f"""
            Người dùng đang chuẩn bị học khóa học '{course_title}' trên nền tảng website '{source_platform}'.
            Hãy biên soạn một cẩm nang hướng dẫn tự học ngắn gọn, thông minh (gồm 3-4 bước thực tế).
            Yêu cầu: Chỉ rõ mẹo để khai thác tốt nhất website này (ví dụ: cách tìm bài tập thực hành trên đó, cách tận dụng forum thảo luận hoặc đọc tài liệu đính kèm của nền tảng {source_platform}).
            Ngôn ngữ: Tiếng Việt. Trực diện, súc tích, trình bày đẹp bằng các gạch đầu dòng (Markdown).
            """
            try:
                # Gọi trực tiếp qua phương thức giao tiếp AI của bạn
                return self.ai._call_ai(prompt)
            except Exception as e:
                print(f"❌ Lỗi sinh cẩm nang học: {e}")
                return f"Hệ thống đã kết nối tới {source_platform}. Bạn hãy nhấn nút 'Mở liên kết' phía trên để học trực tiếp bài học & làm bài tập đi kèm."