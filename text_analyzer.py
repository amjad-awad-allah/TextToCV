import os
import json
import google.generativeai as genai
from openai import OpenAI
from typing import Optional
import time
import copy

def analyze_cv_text(text: str, api_key: str, provider: str = 'gemini', target_language: str = 'German') -> Optional[dict]:
    """
    Verwendet die Gemini API oder OpenAI API, um CV-Daten aus Rohtext in das JSON-Resume-Format zu extrahieren.
    """
    lang_code = "de" if "german" in target_language.lower() or "deutsch" in target_language.lower() else "en"
    prompt = f"""
Du bist ein Experte für die Extraktion von Daten aus Lebensläufen (CV Parser). 
Deine Aufgabe ist es, den unten stehenden Text zu lesen und in ein präzises JSON-Format umzuwandeln, das der (JSON Resume Schema) Struktur entspricht.

Regeln:
1. Extrahiere persönliche Informationen, Berufserfahrung, Ausbildung, Fähigkeiten, Projekte, Sprachen und Zertifikate.
2. Wenn du Links findest (LinkedIn, GitHub, Webseite), setze sie an die richtige Stelle.
3. Die Ausgabesprache MUSS streng in der Zielsprache ({target_language}) sein. Übersetze alle extrahierten Inhalte in diese Sprache.
4. Antworte **NUR** mit validem JSON-Code, ohne zusätzlichen Text, ohne Markdown und ohne Kommentare. Keine Trailing-Commas! Der Schlüssel "language" muss genau "{lang_code}" lauten.
5. Erforderliche Struktur:
   - language: "{lang_code}" 
   - basics: {{ name, email, phone, url, summary, location, profiles: [{{ network, url }}] }}
   - work: [{{ name, position, startDate, endDate, highlights: [] }}]
   - education: [{{ institution, area, studyType, startDate, endDate, courses: [], notes }}]
   - skills: [{{ name, keywords: [] }}]
   - projects: [{{ name, description, highlights: [], keywords: [], url }}]
   - certificates: [{{ name, issuer, date }}]
   - languages: [{{ language, fluency }}]

6. Achte GANZ BESONDERS auf die grammatikalische Korrektheit der Übersetzung und Extraktion. Korrigiere Rechtschreib- und Grammatikfehler aus dem Originaltext. Verwende im Zieltext stets korrekte Artikel (der/die/das) und achte auf eine streng professionelle und fehlerfreie Formulierung.

Zu analysierender Text:
---
{text}
---
"""

    for attempt in range(3):
        try:
            if provider == 'openai':
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Du bist ein Experte für die Extraktion von Daten aus Lebensläufen. Antworte NUR mit validem JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )
                content = response.choices[0].message.content.strip()
            else:
                genai.configure(api_key=api_key)
                try:
                    # Optimized for 2026: Using Gemini 2.5 Flash for fast CV extraction
                    model_name = 'gemini-2.5-flash'
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                except Exception:
                    # Fallback to the latest generic flash alias
                    try:
                        model = genai.GenerativeModel('gemini-flash-latest')
                        response = model.generate_content(prompt)
                    except Exception as e2:
                        raise Exception(f"All models failed. Latest error: {str(e2)}")
                content = response.text.strip()
            break # Success
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                if attempt < 2:
                    time.sleep(5 * (attempt + 1)) # Wait 5, 10 seconds
                    continue
            raise e
        
    if content.startswith("```json"):
        content = content[7:-3].strip()
    elif content.startswith("```"):
        content = content[3:-3].strip()
        
    try:
        data = json.loads(content)
        return data
    except Exception as e:
        raise Exception(f"Fehler bei der KI-Analyse: {str(e)}")

def generate_cover_letter_data(cv_data: dict, job_description: str, api_key: str, provider: str = 'gemini', target_language: str = 'German') -> Optional[dict]:
    cv_data_clean = copy.deepcopy(cv_data)
    if 'basics' in cv_data_clean and 'photo' in cv_data_clean['basics']:
        del cv_data_clean['basics']['photo']
        
    prompt = f"""
Act as a professional Career Coach Expert and formal cover letter writer.

Your task is to write a Cover Letter based on the provided CV data and Job Description.

CRITICAL LANGUAGE RULE: The cover letter MUST be written entirely in the TARGET LANGUAGE ({target_language}). 
- You MUST write the entire cover letter in {target_language}.
IGNORE the language of the Job Description and the CV data when deciding the writing language. ALWAYS use the TARGET LANGUAGE.

⚠️ Strictly follow these rules:

1. Structure:
- Follow a modern professional cover letter structure.
- Salutation (Anrede): Use a specific name only if explicitly mentioned in the job description, otherwise use the standard salutation for the respective language (e.g., "Sehr geehrtes Recruiting-Team" in German or "Dear Hiring Manager" in English).
- First Paragraph (Motivation): Clearly explain why this specific company and this specific role. Do NOT start with generic phrases.
- Second Paragraph (Experience): Mention real practical experience with clear examples and technologies used.
- Third Paragraph (Skill Matching): Directly connect the candidate's skills to the job requirements and demonstrate the ability to learn quickly.
- Last Paragraph (Closing): Mention availability and express a strong desire for an interview.
- Mention salary expectations ONLY if explicitly requested in the job description.
- Close with the standard closing for the respective language (e.g., "Mit freundlichen Grüßen" or "Sincerely").
- Do not repeat the same idea across different paragraphs.

2. Content & Tone:
- Use formal and professional language appropriate to the detected language.
- Do not use generic phrases or clichés.
- Use ONLY information provided in the CV and the Job Description (Do NOT invent or hallucinate data).
- Focus on achievements and business impact rather than just listing tasks.
- Use a clear, direct, and professional tone without filler words.

3. Customization & Optimization:
- Directly link each paragraph to the job requirements.
- Naturally integrate keywords from the job advertisement.
- Optimize the text to be ATS-friendly.
- Use short, clear paragraphs without bullet points.

4. JSON Formatting:
- Provide ONLY valid JSON.
- The "language" key MUST be exactly "{lang_code}".
- NO trailing commas.
- NO comments inside the JSON.

Output the response ONLY in exactly this JSON format:

{{
  "language": "{lang_code}",
  "recipient": {{
    "company": "Company Name",
    "contact_person": "Contact Person",
    "address": "Address",
    "postal_code": "12345",
    "city": "City"
  }},
  "location": "Candidate Location",
  "subject": "Subject",
  "salutation": "Salutation",
  "paragraphs": [
    "Introduction...",
    "Body 1...",
    "Body 2...",
    "Conclusion..."
  ],
  "closing": "Closing"
}}

CV Data:
{json.dumps(cv_data_clean, ensure_ascii=False)}

Job Description:
{job_description}
"""
    for attempt in range(3):
        try:
            if provider == 'openai':
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a Career Specialist and Expert Cover Letter Writer. Answer ONLY with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                content = response.choices[0].message.content.strip()
            else:
                genai.configure(api_key=api_key)
                try:
                    # Using Gemini 2.5 Pro for high-quality cover letter generation
                    model = genai.GenerativeModel('gemini-2.5-pro')
                    response = model.generate_content(prompt)
                except Exception:
                    # Fallback to 2.5 flash
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(prompt)
                content = response.text.strip()
            break # Success
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                if attempt < 2:
                    time.sleep(5 * (attempt + 1))
                    continue
            raise e
            
    if content.startswith("```json"):
        content = content[7:-3].strip()
    elif content.startswith("```"):
        content = content[3:-3].strip()
        
    try:
        data = json.loads(content)
        return data
    except Exception as e:
        raise Exception(f"Fehler bei der KI-Analyse des Anschreibens: {str(e)}")

def rate_cv(cv_text: str, api_key: str, provider: str = 'openai', target_language: str = 'German') -> Optional[str]:
    prompt = f"""
Du bist ein erfahrener, absolut professioneller HR-Experte und Recruiter in Deutschland.
Bewerte den folgenden Lebenslauf basierend auf seiner aktuellen Struktur, Klarheit und Eignung für moderne Bewerbungen (ATS).
Bitte sei absolut ehrlich und streng. Vermeide jegliche unnötigen Schmeicheleien oder Floskeln.
Achte GANZ BESONDERS auf grammatikalische und orthografische Fehler sowie auf den sprachlichen Ausdruck.
Bitte gib dem CV eine realistische Punktzahl von 1 bis 10. Zähle 2-3 echte Stärken sowie 2-3 konkrete Verbesserungsvorschläge auf (inklusive sprachlicher Mängel, falls vorhanden).
Reagiere kurz und bündig (als einfacher Text). Bitte antworte immer auf {target_language}.

Lebenslauf-Text:
{cv_text}
"""
    try:
        for attempt in range(3):
            try:
                if provider == 'openai':
                    client = OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Du bist ein HR-Experte auf Deutsch."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    return response.choices[0].message.content.strip()
                else:
                    genai.configure(api_key=api_key)
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        response = model.generate_content(prompt)
                    except Exception:
                        model = genai.GenerativeModel('gemini-flash-latest')
                        response = model.generate_content(prompt)
                    return response.text.strip()
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    if attempt < 2:
                        time.sleep(5 * (attempt + 1))
                        continue
                raise e
    except Exception as e:
        print(f"Fehler bei der Bewertung: {e}")
        return "Fehler bei der KI-Bewertung."

if __name__ == "__main__":
    openai_key = os.environ.get("OPENAI_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    KEY = openai_key or gemini_key
    provider = 'openai' if openai_key else 'gemini'
    if not KEY:
        print("Bitte setzen Sie die Umgebungsvariable OPENAI_API_KEY oder GEMINI_API_KEY.")