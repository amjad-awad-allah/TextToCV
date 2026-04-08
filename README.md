# 📄 AI CV & Cover Letter Generator (2026 Edition)

An advanced, AI-powered application designed to transform unstructured text into professional, ATS-friendly CVs and tailored Cover Letters. Built with **Python**, **Streamlit**, and **Google Gemini 2.5/3.1**.

### 🔗 [Live Demo - Try it now!](https://txtbewerbung.streamlit.app/)

## 🌟 Features

- **🚀 Smart Extraction**: Upload your old CV (PDF/DOCX/TXT) or paste raw LinkedIn text. The AI extracts work history, skills, and education into a structured JSON Resume format.
- **✉️ Tailored Cover Letters**: Generate German-standard (DIN 5008) cover letters automatically matched to a specific job description.
- **🖼️ Photo Support**: Add a professional profile picture with real-time preview and memory-only storage.
- **🔒 Privacy First**: Zero persistent storage. All data is handled in memory (Session State) and cleared when you close the browser. No more caching issues!
- **🧐 HR Evaluation**: Get expert feedback on your profile and suggestions for improvement.
- **📑 Multinational Export**: Export as standalone CV, Cover Letter, or a combined application package in `.docx` format.
- **🏷️ Version Tracking**: Easily track updates via `version.py` displayed in the app sidebar.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Models**: Google Gemini 2.5 Flash/Pro (with 3.1 fallback)
- **Document Engine**: Python-Docx
- **Parsing**: PyPDF2, python-docx

## 📋 Installation

### 1. Prerequisites
Ensure you have **Python 3.10+** installed.

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/TextToCV.git
cd TextToCV
```

### 3. Set Up Environment
It is recommended to use a virtual environment:
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. API Configuration
For local development, you can enter your API Key directly in the application sidebar. For production, set the `GEMINI_API_KEY` as an environment variable or via your hosting provider's "Secrets" manager.

## 🚀 Usage

Start the application using Streamlit:
```bash
streamlit run app.py
```

### Workflow:
1. **🔍 Extraction**: Upload your file or paste text. Click "Extract" to see the magic.
2. **✍️ CV Editor**: Review and edit the extracted data (Basics, Work, Skills, etc.).
3. **✉️ Cover Letter**: Paste a job description to generate a tailored letter.
4. **💾 Export**: Download your final documents as high-quality Word files.

## 📐 Formatting Standards (German Market)

The generator follows strict German professional standards:
- **CV**: Modern 1-2 page layout with photo support and Calibri typography.
- **Cover Letter**:
  - Salutation followed by comma (DIN 5008).
  - First paragraph starts with a lowercase letter (if grammatically appropriate).
  - Date format: `City, DD.MM.YYYY`.
  - Left-aligned header for consistency.

## 🤝 Contributing
Feel free to open issues or submit pull requests to improve the templates or AI prompts.

---
*Created in 2026 for the next generation of job seekers.*
