import os
import sys
import json
import time
import docx
from docx import Document

print("🔍 Starting Full System Diagnostic Test...")
print("-" * 40)

# 1. Check Dependencies
print("Step 1: Checking Dependencies...")
required_libs = ['streamlit', 'google.generativeai', 'PyPDF2', 'docx', 'dotenv']
missing = []
for lib in required_libs:
    try:
        __import__(lib.replace('-', '_'))
        print(f"✅ {lib} is installed.")
    except ImportError:
        missing.append(lib)

if missing:
    print(f"❌ Missing libraries: {missing}")
else:
    print("✅ All core libraries are present.")

# 2. Check File Utility
print("\nStep 2: Testing File Utilities...")
try:
    import file_utils
    from io import BytesIO
    class MockUploadedFile:
        def __init__(self, name, content):
            self.name = name
            self.content = content
        def read(self): return self.content
    
    test_txt = MockUploadedFile("test.txt", b"Hello CV World")
    extracted = file_utils.extract_text_from_file(test_txt)
    if "Hello CV World" in extracted:
        print("✅ Text extraction from TXT works.")
    else:
        print("❌ Text extraction failed.")
except Exception as e:
    print(f"❌ File utility error: {e}")

# 3. Check Generators (In-Memory Test)
print("\nStep 3: Testing Document Generators (In-Memory)...")
dummy_data = {
    "basics": {"name": "Test User", "email": "test@example.com", "location": {"city": "Stadt", "postalCode": "12345"}},
    "work": [], "education": [], "skills": [], "projects": [], "certificates": [], "languages": []
}
dummy_letter = {
    "recipient": {"company": "Test Co"},
    "salutation": "Sehr geehrte Damen und Herren,",
    "paragraphs": ["This is a test paragraph."],
    "closing": "Mit freundlichen Grüßen",
    "subject": "Test Bewerbung",
    "location": "Stadt"
}

try:
    import cv_generator
    import cover_letter_generator
    import combined_generator
    
    os.makedirs("test_output", exist_ok=True)
    cv_generator.generate_cv(dummy_data, "test_output/test_cv.docx")
    print("✅ CV Generator (In-Memory) works.")
    
    cover_letter_generator.generate_cover_letter(dummy_data, dummy_letter, "test_output/test_cl.docx")
    print("✅ Cover Letter Generator (In-Memory) works.")
    
    combined_generator.generate_combined(dummy_data, dummy_letter, "test_output/test_combined.docx")
    print("✅ Combined Generator (In-Memory) works.")
except Exception as e:
    print(f"❌ Generator error: {e}")

# 4. Check API Key configuration
print("\nStep 4: Checking API Configuration...")
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    print("✅ API Key found in .env file.")
else:
    print("⚠️ No API Key found in .env (User must enter it in Sidebar).")

print("-" * 40)
print("🏁 Diagnostic Complete!")
print("If all '✅' are visible, the project is READY for use.")
print("Run the app with: streamlit run app.py")
