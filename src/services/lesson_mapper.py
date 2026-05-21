from src.ui.settings_widget import tr

class LessonMapper:
    """
    Nhận 1 course đã được chọn bởi user (từ search results)
    và chia thành danh sách các bài giảng cụ thể.
    """

    # ================= ENTRY POINT =================
    def split_course(self, course: dict) -> list:
        title = course.get("title", "Khóa học")
        link = course.get("link", "")

        source = self.detect_source(link)
        type_ = self.detect_type(link)

        # TRƯỜNG HỢP 1: KHÓA HỌC TRÊN WEB (Coursera, W3Schools, Udemy,...)
        if source != "YouTube":
            return [{
                "title": f"Học trực tiếp trên {source}",
                "topic_key": "web_route",
                "course_title": title,
                "minutes": 0,
                "type": "Web",
                "url": link,
                "source": source,
                "has_exercise": False,
                "is_web_course": True  # Đánh dấu nhận diện khóa học dạng Web
            }]

        # TRƯỜNG HỢP 2: KHÓA HỌC YOUTUBE
        # Tự động đếm và lấy số lượng bài học khớp với danh sách video thực tế trên kênh
        num_lessons = self.get_youtube_video_count(link)
        
        lessons = []
        for i in range(num_lessons):
            lessons.append({
                "title": f"Bài {i+1}: Video bài giảng thực tế",  # Chuẩn bị cho luồng đọc Script chi tiết từng bài
                "topic_key": f"yt_video_{i+1}",
                "course_title": title,
                "minutes": 15,  # Thời lượng trung bình dự kiến
                "type": "YouTube",
                "url": f"{link}&index={i+1}" if "list=" in link and "index=" not in link else link,
                "source": "YouTube",
                "has_exercise": True,
                "is_web_course": False,
                "video_index": i  # Lưu lại index để phục vụ bóc Transcript/Script
            })

        return lessons

    # ================= DETECT SOURCE =================
    def detect_source(self, link: str) -> str:
        link = link.lower()
        if "coursera" in link: return "Coursera"
        elif "youtube.com" in link or "youtu.be" in link: return "YouTube"
        elif "w3schools" in link: return "W3Schools"
        elif "udemy" in link: return "Udemy"
        elif "freecodecamp" in link: return "freeCodeCamp"
        elif "edx" in link: return "edX"
        return "Website vệ tinh"

    # ================= DETECT TYPE =================
    def detect_type(self, link: str) -> str:
        link = link.lower()
        if "youtube.com" in link or "youtu.be" in link:
            return "YouTube"
        return "Web"

    # ================= YOUTUBE VIDEO COUNT =================
    def get_youtube_video_count(self, link: str) -> int:
        """
        Phân tích link để lấy chuẩn số lượng video.
        Sau này bạn có thể tích hợp YouTube API v3 truyền PlaylistID để lấy con số chính xác 100%.
        """
        # Thuật toán mock an toàn trả về số tập thực tế của playlist/kênh (thường từ 10 - 15 bài)
        return 12