from src.ui.settings_widget import tr

class LessonMapper:
    """
    Nhận 1 course đã được chọn bởi user (từ search results)
    và chia thành danh sách các bài giảng cụ thể.
    """

    # ================= ENTRY POINT =================
    def split_course(self, course: dict) -> list:
        """
        Nhận 1 dict course {"title": ..., "link": ...}
        Trả về list lessons tương ứng.
        """
        title = course.get("title", "Khóa học")
        link = course.get("link", "")

        source = self.detect_source(link)
        type_ = self.detect_type(link)
        num_lessons = self.get_lesson_count(link)
        keys = self.get_topic_keys(num_lessons)

        lessons = []
        for i, key in enumerate(keys):
            lessons.append({
                "title": title,  # raw
                "topic_key": key,
                "course_title": title,
                "minutes": 10 + i * 5,
                "type": type_,
                "url": link,
                "source": source,
                "has_exercise": (i % 3 == 2),
            })

        return lessons

    # ================= map_to_lessons (dùng cho batch) =================
    # Giữ lại để tương thích với code cũ nếu cần
    def map_to_lessons(self, results: list) -> list:
        lessons = []
        for r in results:
            lessons.extend(self.split_course(r))
        return lessons

    # ================= SỐ LƯỢNG BÀI GIẢNG TÙY NGUỒN =================
    def get_lesson_count(self, link: str) -> int:
        link = link.lower()
        if "coursera" in link:
            return 10
        elif "youtube" in link:
            return 8
        elif "w3schools" in link:
            return 8
        elif "udemy" in link:
            return 10
        elif "freecodecamp" in link:
            return 8
        else:
            return 6

    # ================= DANH SÁCH CHỦ ĐỀ =================
    TOPIC_KEYS = [
        "lesson_intro", "lesson_basic", "lesson_core",
        "lesson_examples", "lesson_demo", "lesson_exercise",
        "lesson_advanced", "lesson_debug", "lesson_best_practice",
        "lesson_summary",
    ]

    def get_topic_keys(self, count: int) -> list:
        return self.TOPIC_KEYS[:count]

    def get_topics(self, count: int) -> list:
        # 10 topic mẫu, cắt theo số lượng cần
        keys = [
            "lesson_intro",
            "lesson_basic",
            "lesson_core",
            "lesson_examples",
            "lesson_demo",
            "lesson_exercise",
            "lesson_advanced",
            "lesson_debug",
            "lesson_best_practice",
            "lesson_summary",
        ]
        return [tr(k) for k in keys[:count]]

    # ================= DETECT SOURCE =================
    def detect_source(self, link: str) -> str:
        link = link.lower()
        if "coursera" in link:
            return "Coursera"
        elif "youtube" in link:
            return "YouTube"
        elif "w3schools" in link:
            return "W3Schools"
        elif "udemy" in link:
            return "Udemy"
        elif "freecodecamp" in link:
            return "freeCodeCamp"
        elif "edx" in link:
            return "edX"
        else:
            return "Online"

    # ================= DETECT TYPE =================
    def detect_type(self, link: str) -> str:
        link = link.lower()
        if "youtube" in link:
            return "Video"
        elif "coursera" in link or "udemy" in link or "edx" in link:
            return "Course"
        elif "w3schools" in link:
            return "Docs"
        else:
            return "Online"