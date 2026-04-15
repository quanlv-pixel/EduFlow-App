import os
import fitz  # PyMuPDF để đọc PDF
from docx import Document # Để đọc Word
import google.generativeai as genai
from dotenv import load_dotenv

class AIEngine:
    def __init__(self):
        # Nạp biến môi trường từ file .env
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        
        # Cấu hình Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def read_pdf(self, file_path):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text

    def read_docx(self, file_path):
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    def get_summary(self, text):
        if not text.strip():
            return "Tài liệu không có nội dung để tóm tắt."
            
        prompt = f"Bạn là một trợ lý học tập. Hãy tóm tắt nội dung sau đây thành các ý chính quan trọng, trình bày bằng gạch đầu dòng rõ ràng, dễ hiểu:\n\n{text}"
        
        response = self.model.generate_content(prompt)
        return response.text