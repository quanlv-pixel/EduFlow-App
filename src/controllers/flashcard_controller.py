class FlashcardController:
    def __init__(self, db, ai):
        self.db = db
        self.ai = ai

    # ================= DECKS =================
    def get_decks(self, user_id: int) -> list:
        return self.db.get_decks(user_id)

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
        """
        cards = self.ai.generate_flashcards_from_topic(prompt)
        return self._save_deck(user_id, title, prompt, cards, source="topic")

    def _save_deck(self, user_id, title, cards_or_prompt, cards=None, source="") -> tuple:
        if cards is None:
            cards = cards_or_prompt
            prompt_text = ""
        else:
            prompt_text = cards_or_prompt

        deck_id = self.db.create_deck(user_id, title, source)
        saved = 0
        for c in cards[:20]:
            q = c.get("q") or c.get("question", "")
            
            # XỬ LÝ CHO TRẮC NGHIỆM YOUTUBE (Nếu câu hỏi có kèm options)
            if "options" in c:
                # Đóng gói câu hỏi và các lựa chọn thành chuỗi đặc biệt ngăn cách bằng dấu |
                options_str = "|".join(c["options"])
                q_saved = f"{q}||options||{options_str}"
                
                # Answer sẽ lưu index của đáp án đúng (ví dụ: "0", "1", "2", "3")
                a_saved = str(c.get("a", 0))
            else:
                # Luồng flashcard truyền thống (mặt trước / mặt sau)
                q_saved = q
                a_saved = c.get("a") or c.get("answer", "")

            if q_saved and a_saved:
                self.db.add_flashcard(user_id, q_saved, a_saved, deck_id)
                saved += 1
        return deck_id, saved

    # Compat cũ
    def generate_ai(self, text: str, lang: str = "vi") -> list:
        return self.ai.generate_flashcards(text, lang=lang)

    def generate_ai_from_text(self, text: str, lang: str = "vi") -> list:
        return self.ai.generate_flashcards(text, lang=lang)

    def generate_ai_from_topic(self, prompt: str, lang: str = "vi") -> list:
        return self.ai.generate_flashcards_from_topic(prompt, lang=lang)
    
    def set_deck_completed(self, deck_id: int, completed=True):
        return self.db.set_deck_completed(deck_id, completed)

    def get_sub_decks(self, user_id: int, parent_id: int) -> list:
        """Controller điều hướng lấy các bộ flashcard bài học nhỏ"""
        return self.db.get_sub_decks(user_id, parent_id)

    def complete_sub_deck(self, deck_id: int) -> bool:
        """Controller điều hướng xử lý hoàn thành bộ trắc nghiệm và tích xanh bài học"""
        return self.db.complete_lesson_flashcard(deck_id)