import requests

class CourseFetcher:
    def __init__(self):
        self.api_key = "d6e6f61b7f729460d0217eee6c12de607cfd275a8da95f63bc97afeaf8a19659" # API của SerApi (Google) để tìm kiếm các khóa học

    def search_courses(self, query):
        url = "https://serpapi.com/search"

        params = {
            # Tìm kiếm khóa học trên Google với từ khóa "course tutorial beginner"
            "q": f"{query} course tutorial beginner",
            "engine": "google",
            "api_key": self.api_key
        }

        try:
            res = requests.get(url, params=params, timeout=20) # Gọi APi để tìm khóa học
            data = res.json() # Chuyển đổi dữ liệu trả về từ API sang JSON để xử lý

            results = []

            for item in data.get("organic_results", [])[:15]:
                link = item.get("link", "")

                if not link:
                    continue

                results.append({
                    "title": item.get("title", ""),
                    "link": link,
                })

            return results

        except Exception as e:
            print("❌ Fetch error:", e)
            return []