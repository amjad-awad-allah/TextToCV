import docx
import PyPDF2
import io

def extract_text_from_file(uploaded_file):
    """
    Extracts text from PDF, DOCX, or TXT files.
    """
    filename = uploaded_file.name.lower()
    
    if filename.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF: {e}"
            
    elif filename.endswith(".docx"):
        try:
            doc = docx.Document(uploaded_file)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            return f"Error reading DOCX: {e}"
            
    elif filename.endswith(".txt"):
        try:
            return uploaded_file.read().decode("utf-8")
        except Exception as e:
            return f"Error reading TXT: {e}"
            
    return "Unsupported file format."
