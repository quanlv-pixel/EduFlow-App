import os
import fitz  # PyMuPDF
from docx import Document
from google import genai
from dotenv import load_dotenv


class AIEngine:
    def __init__(self):
        load_dotenv()

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("❌ Thiếu GOOGLE_API_KEY trong file .env")

        # Init client
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"

    # ================= FILE READER =================
    def read_file(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == ".pdf":
                return self._read_pdf(file_path)
            elif ext == ".docx":
                return self._read_docx(file_path)
            else:
                return "❌ Chỉ hỗ trợ file .pdf và .docx"
        except Exception as e:
            return f"❌ Lỗi đọc file: {str(e)}"

    def _read_pdf(self, file_path):
        text = ""

        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()

            return text.strip() or "❌ File PDF không có nội dung"

        except Exception as e:
            return f"❌ Lỗi đọc PDF: {e}"

    def _read_docx(self, file_path):
        try:
            doc = Document(file_path)
            content = "\n".join([p.text for p in doc.paragraphs])

            return content.strip() or "❌ File Word trống"

        except Exception as e:
            return f"❌ Lỗi đọc Word: {e}"

    # ================= SUMMARY =================
    def get_summary(self, text):
        if not text or len(text.strip()) < 10:
            return "❌ Nội dung quá ngắn để tóm tắt"

        safe_text = text[:30000]

        prompt = f"""
Bạn là trợ lý học tập.

Hãy tóm tắt nội dung sau theo format:

1. Tóm tắt ngắn (2-3 câu)
2. Ý chính (bullet points)
3. Thuật ngữ quan trọng

Ngôn ngữ: Tiếng Việt, rõ ràng, dễ hiểu.

NỘI DUNG:
{safe_text}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

            return response.text or "❌ Không nhận được phản hồi từ AI"

        except Exception as e:
            return f"❌ Lỗi AI: {str(e)}"

    # ================= FLASHCARD AI (ĂN ĐIỂM) =================
    def generate_flashcards(self, text):
        if not text or len(text.strip()) < 20:
            return []

        safe_text = text[:20000]

        prompt = f"""
Tạo flashcard từ nội dung sau.

Trả về dạng JSON:
[
  {{"q": "câu hỏi", "a": "câu trả lời"}},
  ...
]

NỘI DUNG:
{safe_text}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

            raw = response.text

            # parse đơn giản (có thể cải thiện sau)
            import json
            try:
                data = json.loads(raw)
                return data
            except:
                return [{"q": "Lỗi parse", "a": raw}]

        except Exception as e:
            return [{"q": "Lỗi AI", "a": str(e)}]