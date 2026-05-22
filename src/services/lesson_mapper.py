from src.ui.settings_widget import tr
from src.services.youtube_service import YouTubeService


class LessonMapper:
    """
    Nhận 1 course đã được chọn bởi user (từ search results)
    và chia thành danh sách các bài giảng cụ thể.
    """

    def __init__(self):
        try:
            self.yt_service = YouTubeService()
        except Exception as e:
            print(f"[LessonMapper] YouTubeService không khởi tạo được: {e}")
            self.yt_service = None

    # ================= ENTRY POINT =================
    def split_course(self, course: dict) -> list:
        title = course.get("title", "Khóa học")
        link  = course.get("link", "")

        source = self.detect_source(link)

        # TRƯỜNG HỢP 1: KHÓA HỌC TRÊN WEB (Coursera, W3Schools, Udemy,...)
        if source != "YouTube":
            return [{
                "title":         f"Học trực tiếp trên {source}",
                "topic_key":     "web_route",
                "course_title":  title,
                "minutes":       0,
                "type":          "Web",
                "url":           link,
                "source":        source,
                "has_exercise":  False,
                "is_web_course": True,
            }]

        # TRƯỜNG HỢP 2: KHÓA HỌC YOUTUBE — lấy số bài THỰC TẾ từ playlist
        if self.yt_service:
            try:
                videos = self.yt_service.get_lessons_from_url(link)
                if videos:
                    # Bổ sung các trường cần thiết cho DB
                    for i, v in enumerate(videos):
                        v.setdefault("topic_key",    f"yt_video_{i + 1}")
                        v.setdefault("course_title", title)
                        v.setdefault("minutes",      15)
                        v.setdefault("type",         "YouTube")
                        v.setdefault("has_exercise", True)
                        v.setdefault("video_index",  i)
                    return videos
            except Exception as e:
                print(f"[LessonMapper] Lỗi lấy playlist YouTube: {e}")

        # Fallback: không có API key hoặc lỗi → báo trống, không mock
        print("[LessonMapper] ⚠️ Không lấy được bài học từ YouTube. Kiểm tra YOUTUBE_API_KEY.")
        return []

    # ================= DETECT SOURCE =================
    def detect_source(self, link: str) -> str:
        link = link.lower()
        if "youtube.com" in link or "youtu.be" in link: return "YouTube"
        elif "coursera"      in link: return "Coursera"
        elif "w3schools"     in link: return "W3Schools"
        elif "udemy"         in link: return "Udemy"
        elif "freecodecamp"  in link: return "freeCodeCamp"
        elif "edx"           in link: return "edX"
        return "Website"

    # ================= DETECT TYPE =================
    def detect_type(self, link: str) -> str:
        link = link.lower()
        if "youtube.com" in link or "youtu.be" in link:
            return "YouTube"
        return "Web"