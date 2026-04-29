class FlashcardController:
    def __init__(self, db, ai):
        self.db = db
        self.ai = ai

    def get_flashcards(self, user_id):
        return self.db.get_flashcards(user_id)

    def add_flashcard(self, user_id, q, a):
        return self.db.add_flashcard(user_id, q, a)

    def generate_ai_from_text(self, text: str) -> list:
        """Tạo flashcard từ nội dung tài liệu."""
        return self.ai.generate_flashcards(text)

    def generate_ai_from_topic(self, user_prompt: str) -> list:
        """Tạo flashcard từ prompt người dùng (ví dụ: 'tạo flashcard về Python')."""
        return self.ai.generate_flashcards_from_topic(user_prompt)

    # Giữ lại để tương thích với code cũ
    def generate_ai(self, text: str) -> list:
        return self.ai.generate_flashcards(text)