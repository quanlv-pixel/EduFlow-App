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
            "gemini-2.5-flash",         # Bản 2.5 cực kỳ ổn định, ít bị nghẽn hơn bản 3.5
            "gemini-2.5-flash-lite",    # Bản siêu nhẹ, phản hồi tức thì
            "gemini-2.0-flash"          # Phương án dự phòng cuối cùng
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
                    
                    # THÊM DÒNG NÀY ĐỂ BẮT BỆNH:
                    print(f"🚨 LỖI TỪ GOOGLE API (Model {model}): {err}") 
                    
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
    def generate_flashcards(self, text: str, limit: int = 12, lang: str = "vi") -> list:
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

Read the document content below and create effective study flashcards.

Requirements:
- Create exactly {limit} flashcards.
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
        """
        Lấy transcript YouTube nếu có.
        Nếu không lấy được -> AI tự suy luận từ tiêu đề bài học.
        """

        video_id = self.extract_youtube_id(video_url)
        script_text = ""

        if video_id:
            try:
                ytt = YouTubeTranscriptApi()

                # Ưu tiên tiếng Việt -> tiếng Anh -> biến thể tiếng Anh
                transcript_list = ytt.fetch(
                    video_id,
                    languages=[
                        "vi",
                        "en",
                        "en-US",
                        "en-GB",
                        "en-IN"
                    ]
                )

                script_text = " ".join(
                    item.text
                    for item in transcript_list
                )

                print(
                    f"✅ Lấy transcript thành công ({len(script_text)} ký tự)"
                )

            except Exception as e:

                print(
                    f"⚠️ Không thể lấy transcript ({e})"
                )

                print(
                    f"🧠 Fallback AI theo tiêu đề: {lesson_title}"
                )

        # ================= Context =================

        if script_text:

            context_data = f"""
    NỘI DUNG BÀI GIẢNG:

    {script_text[:10000]}
    """

        else:

            context_data = f"""
    TIÊU ĐỀ BÀI HỌC:

    {lesson_title}

    Hãy suy luận nội dung kiến thức có thể xuất hiện
    trong bài học dựa trên tiêu đề.
    """

        # ================= Prompt =================

        prompt = f"""
    Bạn là trợ lý giáo dục AI.

    Dựa trên dữ liệu bên dưới:

    {context_data}

    Hãy tạo từ 5-7 flashcard trắc nghiệm.

    YÊU CẦU:

    1. Bám sát nội dung bài học
    2. Chỉ trả về JSON Array
    3. Không thêm markdown
    4. Không thêm ```json
    5. Toàn bộ bằng tiếng Việt

    Ví dụ:

    [
        {{
            "q":"Python là gì?",
            "options":[
                "Ngôn ngữ lập trình",
                "Hệ điều hành",
                "Database",
                "Trình duyệt"
            ],
            "a":0
        }}
    ]
    """

        raw = self._call_ai(prompt)

        try:

            cleaned = re.sub(
                r"```json|```",
                "",
                raw.strip()
            )

            cards = self._parse_flashcard_json(
                cleaned
            )

            if cards:
                return cards

        except Exception as e:

            print(
                f"❌ Parse flashcard lỗi: {e}"
            )

        # ================= cứu cánh cuối =================

        return [{
            "q": f"{lesson_title} chủ yếu nói về điều gì?",
            "options": [
                lesson_title,
                "Khái niệm không liên quan",
                "Nội dung khác",
                "Đáp án nhiễu"
            ],
            "a":0
        }]
    # ================= TUTORIAL =================
    def generate_tutorial(
            self,
            course_name: str,
            source_platform: str
        ) -> str:

        prompt = f"""
    Bạn là chuyên gia tư vấn học tập.

    Sinh viên muốn tự học "{course_name}"
    trên nền tảng {source_platform}.

    Hãy viết cẩm nang tự học ngắn gọn gồm 4–5 bước,
    phù hợp với {source_platform}.

    Viết bằng tiếng Việt, rõ ràng,
    dùng emoji cho mỗi bước.
    """

        return self._call_ai(prompt)


