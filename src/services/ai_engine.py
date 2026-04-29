import os
import time
import json
import re
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
                    if "503" in err or "UNAVAILABLE" in err:
                        time.sleep(2)
                        continue
                    break

        return f"❌ AI lỗi: {last_error}"

    def _parse_flashcard_json(self, raw: str) -> list:
        """Parse JSON từ response AI, hỗ trợ nhiều format."""
        # Thử tìm array JSON trong response
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            try:
                cards = json.loads(match.group())
                # Chuẩn hoá key: hỗ trợ cả {"q":, "a":} và {"question":, "answer":}
                result = []
                for c in cards:
                    q = c.get("q") or c.get("question", "")
                    a = c.get("a") or c.get("answer", "")
                    if q and a:
                        result.append({"q": str(q), "a": str(a)})
                return result
            except Exception:
                pass
        return []

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

    # ================= FLASHCARD TỪ TÀI LIỆU =================
    def generate_flashcards(self, text: str) -> list:
        """Tạo flashcard từ nội dung tài liệu (PDF/DOCX)."""
        if not text or len(text.strip()) < 50:
            return []

        safe_text = text[:20000]
        prompt = f"""
Bạn là trợ lý học tập thông minh.

Hãy đọc nội dung tài liệu bên dưới và tạo ra 10-15 flashcard ôn tập hiệu quả.

Yêu cầu:
- Mỗi câu hỏi phải rõ ràng, ngắn gọn
- Câu trả lời chính xác, không quá dài (1-3 câu)
- Bao phủ các khái niệm quan trọng nhất trong tài liệu
- Viết bằng Tiếng Việt

Chỉ trả về JSON array, không thêm text nào khác:
[
  {{"q": "Câu hỏi ôn tập?", "a": "Câu trả lời ngắn gọn"}},
  ...
]

TÀI LIỆU:
{safe_text}
"""
        raw = self._call_ai(prompt)
        cards = self._parse_flashcard_json(raw)

        if not cards:
            return [{"q": "❌ Không parse được", "a": raw[:200]}]
        return cards

    # ================= FLASHCARD TỪ TOPIC (MỚI) =================
    def generate_flashcards_from_topic(self, user_prompt: str) -> list:
        """
        Tạo flashcard từ prompt của người dùng.
        Ví dụ: "tạo flashcard về Python", "ôn tập Giải tích"
        """
        if not user_prompt or not user_prompt.strip():
            return []

        prompt = f"""
Bạn là trợ lý học tập thông minh.

Người dùng yêu cầu: "{user_prompt.strip()}"

Hãy tạo ra 10-12 flashcard ôn tập chất lượng cao về chủ đề đó.

Yêu cầu:
- Câu hỏi đa dạng: định nghĩa, ví dụ, so sánh, ứng dụng
- Câu trả lời súc tích, dễ nhớ (1-3 câu)
- Bắt đầu từ cơ bản đến nâng cao
- Viết bằng Tiếng Việt (trừ thuật ngữ chuyên ngành thì giữ nguyên)

Chỉ trả về JSON array, không thêm text nào khác:
[
  {{"q": "Câu hỏi?", "a": "Câu trả lời"}},
  ...
]
"""
        raw = self._call_ai(prompt)
        cards = self._parse_flashcard_json(raw)

        if not cards:
            return [{"q": "❌ Không parse được", "a": raw[:200]}]
        return cards