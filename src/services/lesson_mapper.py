import re


class LessonMapper:
    """
    Nhận 1 course user đã chọn và chia thành các bài giảng.

    - YouTube  → tất cả lesson cùng video_id, hiển thị "Chương X/N"
    - Web      → mỗi lesson có url riêng (nếu xây được) + chú thích bài X đến bài Y
    """

    # ================= ENTRY POINT =================
    def split_course(self, course: dict) -> list:
        title = course.get("title", "Khóa học")
        link  = course.get("link", "")

        source     = self.detect_source(link)
        type_      = self.detect_type(link)
        num        = self.get_lesson_count(link)
        topics     = self.get_topics(num)
        is_youtube = (source == "YouTube")

        # Trích video_id nếu là YouTube
        video_id = self._extract_youtube_id(link) if is_youtube else None

        lessons = []
        for i, topic in enumerate(topics):
            lesson_url = self._build_lesson_url(link, source, topic, i) if not is_youtube else link

            lessons.append({
                "title":        f"{topic}",
                "course_title": title,           # tiêu đề gốc của video/course
                "duration":     f"{10 + i * 5} phút",
                "type":         type_,
                "url":          lesson_url,
                "source":       source,
                "has_exercise": (i % 3 == 2),
                # ── Metadata mới ──
                "lesson_index":  i + 1,          # 1-based
                "total_lessons": num,
                "video_id":      video_id,        # chỉ có với YouTube
                "is_youtube":    is_youtube,
                # Chú thích phạm vi bài học (dành cho web source)
                "web_chapter":   self._web_chapter_label(source, topic, i, num),
            })

        return lessons

    # ================= YOUTUBE ID =================
    def _extract_youtube_id(self, url: str) -> str | None:
        """Trích video ID từ mọi dạng URL YouTube."""
        patterns = [
            r"(?:v=)([0-9A-Za-z_-]{11})",
            r"(?:youtu\.be/)([0-9A-Za-z_-]{11})",
            r"(?:embed/)([0-9A-Za-z_-]{11})",
            r"(?:shorts/)([0-9A-Za-z_-]{11})",
        ]
        for p in patterns:
            m = re.search(p, url)
            if m:
                return m.group(1)
        return None

    # ================= URL CHO TỪNG BÀI (WEB) =================
    def _build_lesson_url(self, base_url: str, source: str, topic: str, index: int) -> str:
        """
        Với các nguồn web có thể đoán được URL sub-page, trả về link cụ thể.
        Nếu không đoán được thì trả về base_url.
        """
        # W3Schools: cấu trúc URL có thể suy ra từ base path
        if source == "W3Schools":
            # Ví dụ base: https://www.w3schools.com/python/
            # → https://www.w3schools.com/python/python_intro.asp
            slug_map = {
                0: "default.asp",       # Giới thiệu & Tổng quan
                1: "python_syntax.asp" if "python" in base_url.lower()
                   else "js_syntax.asp" if "js" in base_url.lower()
                   else "default.asp",  # Kiến thức nền tảng
                2: "python_variables.asp" if "python" in base_url.lower()
                   else "default.asp",  # Khái niệm cốt lõi
            }
            slug = slug_map.get(index, "default.asp")
            # Xây URL tuyệt đối
            base = base_url.rstrip("/") + "/"
            return base + slug

        # freeCodeCamp: dùng base_url, không có sub-page cố định
        # Coursera / Udemy / edX: URL khoá học, không tự xây sub-page
        return base_url

    # ================= NHÃN CHÚ THÍCH BÀI HỌC (WEB) =================
    def _web_chapter_label(self, source: str, topic: str, index: int, total: int) -> str:
        """
        Sinh chuỗi chú thích hiển thị trong LessonItem.
        Ví dụ: "Bài 1/8  •  Giới thiệu & Tổng quan  •  W3Schools"
        """
        return f"Bài {index + 1}/{total}  •  {topic}  •  {source}"

    # ================= TOPICS =================
    def get_topics(self, count: int) -> list:
        all_topics = [
            "Giới thiệu & Tổng quan",
            "Kiến thức nền tảng",
            "Khái niệm cốt lõi",
            "Ví dụ minh họa thực tế",
            "Ứng dụng & Demo",
            "Bài tập thực hành",
            "Chuyên sâu & Nâng cao",
            "Debug & Xử lý lỗi phổ biến",
            "Best Practices",
            "Tổng kết & Ôn tập",
        ]
        return all_topics[:count]

    # ================= LESSON COUNT =================
    def get_lesson_count(self, link: str) -> int:
        link = link.lower()
        if "coursera" in link:   return 10
        if "youtube"  in link:   return 8
        if "w3schools" in link:  return 8
        if "udemy"    in link:   return 10
        if "freecodecamp" in link: return 8
        return 6

    # ================= DETECT SOURCE =================
    def detect_source(self, link: str) -> str:
        link = link.lower()
        if "youtube" in link or "youtu.be" in link: return "YouTube"
        if "coursera"     in link: return "Coursera"
        if "w3schools"    in link: return "W3Schools"
        if "udemy"        in link: return "Udemy"
        if "freecodecamp" in link: return "freeCodeCamp"
        if "edx"          in link: return "edX"
        if "mdn"          in link or "developer.mozilla" in link: return "MDN"
        return "Online"

    # ================= DETECT TYPE =================
    def detect_type(self, link: str) -> str:
        link = link.lower()
        if "youtube" in link or "youtu.be" in link: return "Video"
        if "coursera" in link or "udemy" in link or "edx" in link: return "Course"
        if "w3schools" in link or "mdn" in link:    return "Docs"
        return "Online"

    # ================= BATCH COMPAT =================
    def map_to_lessons(self, results: list) -> list:
        lessons = []
        for r in results:
            lessons.extend(self.split_course(r))
        return lessons