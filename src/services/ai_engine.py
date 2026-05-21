import os
import time
import json
import re
import fitz
from docx import Document
from google import genai
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi


class AIEngine:
    def __init__(self):
        load_dotenv()

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("❌ Thiếu GOOGLE_API_KEY trong .env")

        self.client = genai.Client(api_key=api_key)
        self.models = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
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
        """Hàm parse chung bóc tách mảng JSON từ phản hồi của AI"""
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            try:
                cards = json.loads(match.group())
                result = []
                for c in cards:
                    q = c.get("q") or c.get("question", "")
                    
                    # Hỗ trợ cả 2 luồng: 
                    # 1. Luồng trắc nghiệm mới (a là index số nguyên, có options)
                    # 2. Luồng flashcard cũ (a là một chuỗi văn bản câu trả lời phẳng)
                    options = c.get("options")
                    a_val = c.get("a") if c.get("a") is not None else c.get("answer")
                    
                    if q and a_val is not None:
                        if options and isinstance(options, list):
                            # Luồng câu hỏi dạng trắc nghiệm 4 lựa chọn
                            result.append({
                                "q": str(q),
                                "options": [str(opt) for opt in options],
                                "a": a_val # Giữ nguyên index integer (0, 1, 2, 3)
                            })
                        else:
                            # Luồng Flashcard truyền thống
                            result.append({
                                "q": str(q),
                                "a": str(a_val)
                            })
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
    def generate_flashcards(self, text: str, lang: str = "vi") -> list:
        if not text or len(text.strip()) < 50:
            return []

        lang_map = {
            "vi": "Tiếng Việt",
            "en": "English",
            "cn": "中文（简体）",
        }
        output_lang = lang_map.get(lang, "Tiếng Việt")

        safe_text = text[:20000]
        prompt = f"""
You are a smart study assistant.

Read the document content below and create 10-15 effective study flashcards.

Requirements:
- Each question must be clear and concise
- Answers must be accurate, not too long (1-3 sentences)
- Cover the most important concepts in the document
- Write ALL questions and answers in {output_lang}
- Keep technical/specialized terms as-is if they have no natural translation

Return ONLY a JSON array, no extra text:
[
  {{"q": "Question?", "a": "Short answer"}},
  ...
]

DOCUMENT:
{safe_text}
"""
        raw = self._call_ai(prompt)
        cards = self._parse_flashcard_json(raw)

        if not cards:
            return [{"q": "❌ Không parse được", "a": raw[:200]}]
        return cards

    # ================= FLASHCARD TỪ TOPIC (MỚI) =================
    def generate_flashcards_from_topic(self, user_prompt: str, lang: str = "vi") -> list:
        if not user_prompt or not user_prompt.strip():
            return []

        lang_map = {
            "vi": "Tiếng Việt",
            "en": "English",
            "cn": "中文（简体）",
        }
        output_lang = lang_map.get(lang, "Tiếng Việt")

        prompt = f"""
You are a smart study assistant.

User request: "{user_prompt.strip()}"

Create 10-12 high-quality study flashcards on that topic.

Requirements:
- Diverse questions: definitions, examples, comparisons, applications
- Concise, memorable answers (1-3 sentences)
- Progress from basic to advanced
- Write ALL questions and answers in {output_lang}
- Keep technical/specialized terms as-is if they have no natural translation

Return ONLY a JSON array, no extra text:
[
  {{"q": "Question?", "a": "Answer"}},
  ...
]
"""
        raw = self._call_ai(prompt)
        cards = self._parse_flashcard_json(raw)

        if not cards:
            return [{"q": "❌ Không parse được", "a": raw[:200]}]
        return cards

    # ================= SCRIPT YOUTUBE & TRẮC NGHIỆM KHÓA HỌC =================
    def extract_youtube_id(self, url: str) -> str:
        if not url:
            return None
        patterns = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        match = re.search(patterns, url)
        return match.group(1) if match else None

    def generate_flashcards_from_youtube(self, video_url: str, lesson_title: str) -> list:
        """Cào script từ YouTube và bắt Gemini tạo bộ trắc nghiệm dựa trên bài giảng"""
        video_id = self.extract_youtube_id(video_url)
        script_text = ""

        if video_id:
            try:
                # Thử lấy phụ đề tiếng Việt trước, nếu không có thì lấy tiếng Anh
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['vi', 'en'])
                script_text = " ".join([item['text'] for item in transcript])
            except Exception as e:
                print(f"⚠️ Không thể tự động lấy phụ đề từ YouTube ({e}). AI sẽ tự suy luận dựa trên tiêu đề bài học.")
        
        # Nếu lấy được script thì nhồi vào prompt, nếu không lấy được thì dùng tiêu đề bài học để cứu cánh
        context_data = f"NỘI DUNG BÀI GIẢNG (SCRIPT DƯỚI VIDEO):\n{script_text}" if script_text else f"Tiêu đề bài học: {lesson_title}"

        prompt = f"""
Bạn là một trợ lý giáo dục thông minh chuyên về Flashcard.
Dựa vào tài liệu bài học cụ thể được cung cấp dưới đây, hãy soạn ra chính xác từ 5 đến 7 câu hỏi trắc nghiệm kiến thức cốt lõi.

{context_data}

YÊU CẦU BẮT BUỘC:
1. Câu hỏi phải bám rất sát nội dung bài học được cung cấp.
2. Định dạng đầu ra bắt buộc phải là một chuỗi JSON Array sạch duy nhất, không chứa ký hiệu ```json hay bất kỳ chữ giải thích nào bên ngoài.
3. Cấu trúc mỗi phần tử trong Array phải giống hoàn toàn như sau:
[
  {{
    "q": "Câu hỏi trắc nghiệm cụ thể ?",
    "options": ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"],
    "a": 0
  }}
]
Trong đó "options" là mảng gồm 4 đáp án lựa chọn, và "a" là CHỈ SỐ INDEX của đáp án đúng (0 cho đáp án đầu tiên, 1 cho đáp án thứ hai, v.v.). Toàn bộ viết bằng Tiếng Việt.
"""
        raw = self._call_ai(prompt)

        try:
            cleaned = re.sub(
                r'^(?:https?://googleusercontent\.com/immersive_entry_chip/json)?\s*```?|```?\s*$',
                '',
                raw.strip(),
                flags=re.MULTILINE
            )

            cards = self._parse_flashcard_json(cleaned)

            if cards:
                return cards

        except Exception as e:
            print("❌ Lỗi parse JSON Flashcard từ YouTube:", e)

        return [
            {
                "q": f"Kiến thức cốt lõi của bài học: {lesson_title}",
                "options": [
                    "Đáp án đúng mẫu",
                    "Đáp án nhiễu 1",
                    "Đáp án nhiễu 2",
                    "Đáp án nhiễu 3"
                ],
                "a": 0
            }
        ]


