import os
import fitz  # PyMuPDF
from docx import Document
from google import genai  # Thư viện mới nhất
from dotenv import load_dotenv

class AIEngine:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        
        # Khởi tạo Client theo chuẩn SDK 2026
        self.client = genai.Client(api_key=api_key)
        
        # Sử dụng model mạnh nhất và nhanh nhất Quân vừa quét được
        self.model_name = "gemini-2.5-flash"

    def read_file(self, file_path):
        """Tự động nhận diện và đọc nội dung từ file PDF hoặc Word"""
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.pdf':
                return self._read_pdf(file_path)
            elif ext == '.docx':
                return self._read_docx(file_path)
            return "Định dạng file này hiện chưa được hỗ trợ."
        except Exception as e:
            return f"Lỗi kỹ thuật khi đọc file: {str(e)}"

    def _read_pdf(self, file_path):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text if text.strip() else "File PDF này không có nội dung văn bản (có thể là file ảnh)."

    def _read_docx(self, file_path):
        doc = Document(file_path)
        content = "\n".join([para.text for para in doc.paragraphs])
        return content if content.strip() else "File Word này trống."

    def get_summary(self, text):
        """Gửi văn bản lên AI và lấy bản tóm tắt chất lượng cao"""
        if not text.strip() or len(text) < 20:
            return "Văn bản quá ngắn hoặc không có nội dung để tóm tắt."
        
        # Giới hạn nội dung để tránh quá tải (Flash hỗ trợ rất dài nhưng 15k là ổn cho Edu)
        clean_text = text[:20000] 
        
        # Prompt được tối ưu để AI phản hồi chuyên nghiệp hơn
        prompt = (
            "Bạn là một trợ lý học tập thông minh. Hãy tóm tắt văn bản sau đây "
            "một cách súc tích, rõ ràng bằng tiếng Việt. "
            "Yêu cầu: \n"
            "- Sử dụng các gạch đầu dòng cho các ý chính.\n"
            "- Giữ lại các thuật ngữ quan trọng.\n"
            "- Kết thúc bằng một câu nhận xét về độ hữu ích của tài liệu này.\n\n"
            f"NỘI DUNG VĂN BẢN:\n{clean_text}"
        )
        
        try:
            # Gọi API theo cú pháp mới của google-genai
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Lỗi khi kết nối với AI: {str(e)}"