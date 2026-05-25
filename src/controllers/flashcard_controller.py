class FlashcardController:
    def __init__(self, db, ai):
        self.db = db
        self.ai = ai

    # ================= DECKS =================
    def get_decks(self, user_id: int) -> list:
        """Lấy tất cả decks (dùng nội bộ hoặc khi cần đủ)."""
        return self.db.get_decks(user_id)

    def get_user_decks(self, user_id: int) -> list:
        """
        Chỉ lấy decks từ mục Flashcard (file hoặc AI tự tạo).
        KHÔNG bao gồm deck từ khóa học (source='course').
        """
        all_decks = self.db.get_decks(user_id)
        return [d for d in all_decks if d.get("source") != "course"]

    def get_course_decks(self, user_id: int) -> list:
        """
        Lấy các deck CHA đại diện cho từng khóa học (parent_id IS NULL, source='course').
        Dùng cho màn "Từ khóa học" trong FlashcardWidget.
        """
        all_decks = self.db.get_decks(user_id)
        return [
            d for d in all_decks
            if d.get("source") == "course" and d.get("parent_id") is None
        ]

    def delete_deck(self, deck_id: int):
        return self.db.delete_deck(deck_id)

    # ================= CARDS =================
    def get_flashcards(self, user_id: int, deck_id: int = None) -> list:
        return self.db.get_flashcards(user_id, deck_id)

    def add_flashcard(self, user_id: int, q: str, a: str, deck_id: int = None):
        return self.db.add_flashcard(user_id, q, a, deck_id)

    def delete_flashcard(self, card_id: int):
        return self.db.delete_flashcard(card_id)

    # ================= AI TẠO DECK MỚI =================
    def create_deck_from_text(self, user_id: int, title: str, text: str) -> tuple[int, int]:
        """
        Tạo deck mới từ nội dung file.
        Trả về (deck_id, số card đã lưu).
        """
        cards = self.ai.generate_flashcards(text)
        return self._save_deck(user_id, title, cards, source="file")

    def create_deck_from_topic(self, user_id: int, title: str, prompt: str) -> tuple[int, int]:
        """
        Tạo deck mới từ prompt người dùng.
        Trả về (deck_id, số card đã lưu).

        FIX: Phiên bản cũ truyền nhầm `prompt` vào vị trí `cards` của _save_deck,
        dẫn đến lỗi TypeError khi _save_deck duyệt qua string thay vì list.
        """
        cards = self.ai.generate_flashcards_from_topic(prompt)
        return self._save_deck(user_id, title, cards, source="topic")

    def _save_deck(self, user_id, title, cards, source="",
                   lesson_id=None, parent_id=None) -> tuple:
        """
        Lưu deck + cards vào DB.
        FIX: Thêm tham số lesson_id và parent_id để hỗ trợ cấu trúc deck khóa học.
        """
        deck_id = self.db.create_deck(user_id, title, source, lesson_id=lesson_id)

        # Gán parent_id nếu có (deck bài học con thuộc deck khóa học cha)
        if parent_id is not None:
            self.db.execute(
                "UPDATE flashcard_decks SET parent_id=? WHERE id=?",
                (parent_id, deck_id)
            )

        saved = 0
        for c in cards[:20]:
            q = c.get("q") or c.get("question", "")

            # XỬ LÝ CHO TRẮC NGHIỆM YOUTUBE (Nếu câu hỏi có kèm options)
            if "options" in c:
                options_str = "|".join(c["options"])
                q_saved = f"{q}||options||{options_str}"
                a_saved = str(c.get("a", 0))
            else:
                q_saved = q
                a_saved = c.get("a") or c.get("answer", "")

            if q_saved and a_saved:
                self.db.add_flashcard(user_id, q_saved, a_saved, deck_id)
                saved += 1

        return deck_id, saved

    # ================= DECK KHÓA HỌC =================
    def ensure_course_parent_deck(self, user_id, course_id, course_name):

        existing=self.db.execute(
            """
            SELECT id
            FROM flashcard_decks
            WHERE
            user_id=?
            AND course_id=?
            AND parent_id IS NULL
            AND source='course'
            """,
            (
                user_id,
                course_id
            ),
            fetch=True
        )

        if existing:
            return existing[0]["id"]

        return self.db.create_deck(
            user_id,
            course_name,
            source="course",
            parent_id=None,
            course_id=course_id
        )

    def get_sub_decks(self, user_id: int, parent_id: int) -> list:
        """Lấy các deck BÀI HỌC con thuộc deck khóa học cha."""
        return self.db.get_sub_decks(user_id, parent_id)

    def complete_sub_deck(self, deck_id: int) -> bool:
        """Đánh dấu hoàn thành bộ flashcard bài học và tích xanh bài học liên kết."""
        return self.db.complete_lesson_flashcard(deck_id)

    def set_deck_completed(self, deck_id: int, completed=True):
        return self.db.set_deck_completed(deck_id, completed)

    # ================= COMPAT CŨ =================
    def generate_ai(self, text: str, lang: str = "vi") -> list:
        return self.ai.generate_flashcards(text, lang=lang)

    def generate_ai_from_text(self, text: str, lang: str = "vi") -> list:
        return self.ai.generate_flashcards(text, lang=lang)

    def generate_ai_from_topic(self, prompt: str, lang: str = "vi") -> list:
        return self.ai.generate_flashcards_from_topic(prompt, lang=lang)