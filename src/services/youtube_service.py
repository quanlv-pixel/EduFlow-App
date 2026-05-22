import os
import re
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

class YouTubeService:
    def __init__(self):
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            raise ValueError("Thiếu YOUTUBE_API_KEY trong file .env")
        self.youtube = build("youtube", "v3", developerKey=api_key)

    def extract_playlist_id(self, url: str) -> str | None:
        """Lấy playlist ID từ URL dạng ?list=PLxxx"""
        match = re.search(r"[?&]list=([a-zA-Z0-9_-]+)", url)
        return match.group(1) if match else None

    def get_videos_from_playlist(self, playlist_id: str) -> list[dict]:
        """
        Gọi YouTube API, lấy TOÀN BỘ video trong playlist.
        Tự xử lý phân trang nếu playlist > 50 video.
        """
        videos = []
        next_page_token = None

        while True:
            resp = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            for item in resp.get("items", []):
                snippet = item["snippet"]
                video_id = snippet["resourceId"]["videoId"]

                # Bỏ qua video bị xóa/riêng tư
                if snippet.get("title") in ("Deleted video", "Private video"):
                    continue

                videos.append({
                    "title":        snippet["title"],
                    "url":          f"https://www.youtube.com/watch?v={video_id}",
                    "video_id":     video_id,
                    "thumbnail":    snippet.get("thumbnails", {})
                                           .get("medium", {})
                                           .get("url", ""),
                    "position":     snippet.get("position", 0),  # thứ tự trong playlist
                    "is_web_course": False,
                    "source":       "YouTube",
                })

            next_page_token = resp.get("nextPageToken")
            if not next_page_token:
                break

        # Sắp xếp theo đúng thứ tự playlist
        videos.sort(key=lambda v: v["position"])
        return videos

    def get_lessons_from_url(self, url: str) -> list[dict]:
            """Hàm tổng — tự nhận diện playlist hoặc video đơn."""
            # 1. Thử bóc tách theo dạng Playlist
            playlist_id = self.extract_playlist_id(url)
            if playlist_id:
                return self.get_videos_from_playlist(playlist_id)
                
            # 2. Nếu không phải playlist, thử lấy Video ID đơn lẻ (FALLBACK)
            video_match = re.search(r"(?:v=|/)([0-9A-Za-z_-]{11}).*", url)
            if video_match:
                video_id = video_match.group(1)
                # Khởi tạo 1 bài học duy nhất cho video này
                return [{
                    "title": "Bài học Video độc lập", # Tiêu đề mặc định
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "video_id": video_id,
                    "position": 0,
                    "is_web_course": False,
                    "source": "YouTube",
                }]
                
            return []