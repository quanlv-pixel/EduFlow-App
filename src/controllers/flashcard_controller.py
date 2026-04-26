class FlashcardController:
    def __init__(self, db, ai):
        self.db = db
        self.ai = ai

    def get_flashcards(self, user_id):
        return self.db.get_flashcards(user_id)

    def add_flashcard(self, user_id, q, a):
        return self.db.add_flashcard(user_id, q, a)

    def generate_ai(self, text):
        return self.ai.generate_flashcards(text)