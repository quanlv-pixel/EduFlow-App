class SummaryController:
    def __init__(self, ai, db):
        self.ai = ai
        self.db = db

    def read_file(self, path):
        return self.ai.read_file(path)

    def summarize(self, content):
        return self.ai.get_summary(content)

    def save(self, user_id, filename, content, summary):
        return self.db.save_document_and_summary(
            user_id, filename, content, summary
        )
    def get_documents(self, user_id):
        return self.db.get_documents(user_id)
    
    def get_document_detail(self, doc_id):
        return self.db.get_document_detail(doc_id)


    def delete_document(self, doc_id):
        return self.db.delete_document(doc_id)