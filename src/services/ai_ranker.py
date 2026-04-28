class AIRanker:

    def score(self, item):
        score = 0

        title = item.get("title", "").lower()
        link = item.get("link", "").lower()

        # ===== SOURCE =====
        if "coursera" in link:
            score += 5
        elif "freecodecamp" in link:
            score += 4
        elif "w3schools" in link:
            score += 3
        elif "youtube" in link:
            score += 2
        else:
            score += 1  # nguồn lạ

        # ===== KEYWORDS =====
        if "complete" in title or "full course" in title:
            score += 3

        if "beginner" in title:
            score += 2

        if "advanced" in title:
            score += 1

        # ===== LOẠI RÁC =====
        if "login" in link or len(title) < 10:
            return -1

        return score

    def rank(self, results):
        scored = []

        for r in results:
            s = self.score(r)

            if s > 0:
                r["score"] = s
                scored.append(r)

        # sort giảm dần
        scored.sort(key=lambda x: x["score"], reverse=True)

        return scored[:7]