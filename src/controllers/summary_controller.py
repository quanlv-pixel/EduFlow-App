class SummaryController:
    def __init__(self, ai, db):
        self.ai = ai
        self.db = db

    def read_file(self, path):
        return self.ai.read_file(path)

    def summarize(self, text):
        return self.ai.get_summary(text)

    def save(self, user_id, filename, content, summary):
        return self.db.save_document_and_summary(
            user_id, filename, content, summary
        )