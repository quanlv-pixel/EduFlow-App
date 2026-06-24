import os
from google import genai
from dotenv import load_dotenv

# Load API Key từ file .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Không tìm thấy API Key!")
else:
    print("✅ Đang quét danh sách các Model mà API Key của bạn được phép dùng...\n")
    client = genai.Client(api_key=api_key)
    
    # Lấy và in ra toàn bộ tên các Model hỗ trợ Generate Content
    for model in client.models.list():
        if "generateContent" in model.supported_actions:
            # Chỉ in ra phần tên sau chữ 'models/'
            print(f"- {model.name.replace('models/', '')}")