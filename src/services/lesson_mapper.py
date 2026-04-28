class LessonMapper:

    def map_to_lessons(self, results):
        lessons = []

        for i, r in enumerate(results):
            lessons.append({
                "title": r.get("title", f"Lesson {i+1}"),
                "duration": "15-60 phút",
                "type": self.detect_type(r.get("link", "")),
                "url": r.get("link", ""),
                "has_exercise": False
            })

        return lessons

    def detect_type(self, link):
        link = link.lower()

        if "youtube" in link:
            return "Video"
        elif "coursera" in link:
            return "Course"
        elif "w3schools" in link:
            return "Docs"
        elif "udemy" in link:
            return "Course"
        else:
            return "Online"