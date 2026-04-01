import os
import sys
import json
from dotenv import load_dotenv
import text_analyzer
import cv_generator
from typing import Optional

def main():
    load_dotenv()
    raw_file = "raw_cv.txt"
    json_file = "data.json"
    output_docx = "Generated_CV.docx"
    
    # 1. Ask for API Key if not set
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Please set your GEMINI_API_KEY first.")
        print("Example (Windows): set GEMINI_API_KEY=your_key_here")
        print("Example (Linux/Mac): export GEMINI_API_KEY=your_key_here")
        return

    # 2. Extract Data from Raw Text
    if not os.path.exists(raw_file):
        print(f"Error: {raw_file} not found. Please create it and paste your CV text.")
        return
        
    print(f"Reading {raw_file}...")
    with open(raw_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    print("--- [ المرحله الأولى: تحليل النص بالذكاء الاصطناعي ] ---")
    extracted_data = text_analyzer.analyze_cv_text(raw_text, api_key)
    
    if not extracted_data:
        print("Failed to extract data correctly.")
        return

    # 3. Confirmation step
    print("AI has successfully extracted the data.")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
    print(f"Data saved to {json_file}")
    
    confirm = input("Do you want to generate the Word document now? (y/n): ")
    if confirm.lower() != 'y':
        print("Process aborted. You can modify data.json and run the generator manually.")
        return

    # 4. Generate DOCX
    print("--- [ المرحله الثانية: توليد ملف الوورد ] ---")
    cv_generator.generate_cv(json_file, output_docx)

if __name__ == "__main__":
    main()
