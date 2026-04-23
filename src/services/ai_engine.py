import os
import time
import fitz
from docx import Document
from google import genai
from dotenv import load_dotenv


class AIEngine:
    def __init__(self):
        load_dotenv()

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("❌ Thiếu GOOGLE_API_KEY trong .env")

        self.client = genai.Client(api_key=api_key)

        # 👉 ưu tiên model nhanh trước
        self.models = [
            "gemini-1.5-flash",
            "gemini-2.5-flash"
        ]

    # ================= FILE =================
    def read_file(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return self._read_pdf(file_path)
        elif ext == ".docx":
            return self._read_docx(file_path)

        return "❌ Chỉ hỗ trợ PDF hoặc DOCX"

    def _read_pdf(self, file_path):
        try:
            text = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()

            return text.strip() or "❌ PDF không có nội dung"

        except Exception as e:
            return f"❌ Lỗi đọc PDF: {e}"

    def _read_docx(self, file_path):
        try:
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)

        except Exception as e:
            return f"❌ Lỗi DOCX: {e}"

    # ================= CORE AI =================
    def _call_ai(self, prompt, max_retry=3):
        last_error = ""

        for model in self.models:
            for attempt in range(max_retry):
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt
                    )

                    if response and response.text:
                        return response.text

                except Exception as e:
                    err = str(e)
                    last_error = err

                    # 👉 lỗi server → retry
                    if "503" in err or "UNAVAILABLE" in err:
                        time.sleep(2)
                        continue

                    # 👉 lỗi khác → break luôn
                    break

        return f"❌ AI lỗi: {last_error}"

    # ================= SUMMARY =================
    def get_summary(self, text):
        if not text or len(text.strip()) < 20:
            return "❌ Nội dung quá ngắn"

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

        return self._call_ai(prompt)

    # ================= FLASHCARD =================
    def generate_flashcards(self, text):
        if not text or len(text.strip()) < 50:
            return []

        safe_text = text[:20000]

        prompt = f"""
            Tạo flashcard từ nội dung sau.

            Trả về JSON:
            [
            {{"q": "...", "a": "..."}}
            ]

            NỘI DUNG:
            {safe_text}
        """

        raw = self._call_ai(prompt)

        # 👉 parse thông minh
        import json, re

        match = re.search(r"\[.*\]", raw, re.DOTALL)

        if match:
            try:
                return json.loads(match.group())
            except:
                pass

        return [{"q": "Lỗi parse", "a": raw}]