import requests


class CourseFetcher:
    def __init__(self):
        self.api_key = "d6e6f61b7f729460d0217eee6c12de607cfd275a8da95f63bc97afeaf8a19659"

    def search_courses(self, query):
        url = "https://serpapi.com/search"

        params = {
            "q": f"{query} course tutorial beginner",
            "engine": "google",
            "api_key": self.api_key
        }

        try:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()

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