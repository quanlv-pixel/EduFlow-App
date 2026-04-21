class FlashcardController:
    def __init__(self, db, ai):
        self.db = db
        self.ai = ai

    def get_flashcards(self, user_id):
        return self.db.get_flashcards(user_id)

    def add_flashcard(self, user_id, q, a):
        return self.db.add_flashcard(user_id, q, a)

    def generate_ai(self, user_id):
        text = "Python basics variables loops functions"
        
        prompt = f"Tạo 5 flashcard dạng Q&A từ nội dung: {text}"

        res = self.ai.client.models.generate_content(
            model=self.ai.model_name,
            contents=prompt
        )

        # demo parse
        return [
            {"q": "Variable là gì?", "a": "Biến lưu dữ liệu"},
            {"q": "Loop là gì?", "a": "Vòng lặp"}
        ]