import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("--- DANH SÁCH CÁC MODEL BẠN ĐƯỢC PHÉP DÙNG ---")
try:
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Model: {m.name}")
            available_models.append(m.name)
    
    if available_models:
        print("\n--- ĐANG THỬ CHẠY MODEL ĐẦU TIÊN TRONG DANH SÁCH ---")
        test_model = genai.GenerativeModel(available_models[0])
        res = test_model.generate_content("Chào bạn!")
        print(f"AI phản hồi: {res.text}")
    else:
        print("❌ Không tìm thấy model nào khả dụng cho API Key này.")
except Exception as e:
    print(f"❌ Lỗi hệ thống: {e}")