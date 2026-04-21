import os
import fitz  # PyMuPDF
from docx import Document
from google import genai  # CHUẨN MỚI 2026
from dotenv import load_dotenv

class AIEngine:
    def __init__(self):
        # 1. Tải các biến môi trường từ file .env
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        
        # 2. Khởi tạo Client theo thư viện google-genai mới nhất
        # Không còn dùng genai.configure() nữa
        self.client = genai.Client(api_key=api_key)
        
        # 3. Sử dụng model 2.5 Flash Quân đã quét thành công
        self.model_name = "gemini-2.5-flash"

    def read_file(self, file_path):
        """Tự động đọc nội dung từ file PDF hoặc Word"""
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.pdf':
                return self._read_pdf(file_path)
            elif ext == '.docx':
                return self._read_docx(file_path)
            return "Định dạng file không hỗ trợ (Chỉ nhận .pdf và .docx)."
        except Exception as e:
            return f"Lỗi khi đọc file: {str(e)}"

    def _read_pdf(self, file_path):
        """Trích xuất văn bản từ file PDF"""
        text = ""
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
            return text if text.strip() else "File PDF này không có nội dung văn bản."
        except Exception as e:
            return f"Lỗi đọc PDF: {e}"

    def _read_docx(self, file_path):
        """Trích xuất văn bản từ file Word"""
        try:
            doc = Document(file_path)
            content = "\n".join([para.text for para in doc.paragraphs])
            return content if content.strip() else "File Word này trống."
        except Exception as e:
            return f"Lỗi đọc Word: {e}"

    def get_summary(self, text):
        """Gửi văn bản lên Gemini 2.5 Flash để tóm tắt"""
        if not text or len(text.strip()) < 10:
            return "Nội dung quá ngắn để có thể tóm tắt."

        # Cắt bớt văn bản nếu quá dài (Gemini 2.5 Flash chịu được rất nhiều, 30k là thoải mái)
        safe_text = text[:30000]

        # Prompt được thiết kế chuyên sâu cho sinh viên
        prompt = (
            "Bạn là một chuyên gia tóm tắt tài liệu học tập. "
            "Hãy tóm tắt văn bản dưới đây theo cấu trúc:\n"
            "1. Tóm tắt ngắn gọn mục tiêu chính (2-3 câu).\n"
            "2. Danh sách các ý chính quan trọng nhất (dùng gạch đầu dòng).\n"
            "3. Giải thích nhanh các thuật ngữ chuyên môn (nếu có).\n"
            "Yêu cầu: Ngôn ngữ chuyên nghiệp, trình bày rõ ràng bằng tiếng Việt.\n\n"
            f"NỘI DUNG CẦN TÓM TẮT:\n{safe_text}"
        )

        try:
            # CẤU TRÚC GỌI API MỚI NHẤT
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            # Trả về nội dung tóm tắt
            return response.text
        except Exception as e:
            return f"Lỗi khi gọi AI: {str(e)}"
