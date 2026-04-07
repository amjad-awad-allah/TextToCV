import os
import json
import google.generativeai as genai
from openai import OpenAI
from typing import Optional

def analyze_cv_text(text: str, api_key: str, provider: str = 'gemini') -> Optional[dict]:
    """
    Verwendet die Gemini API oder OpenAI API, um CV-Daten aus Rohtext in das JSON-Resume-Format zu extrahieren.
    """
    prompt = f"""
Du bist ein Experte für die Extraktion von Daten aus Lebensläufen (CV Parser). 
Deine Aufgabe ist es, den unten stehenden Text zu lesen und in ein präzises JSON-Format umzuwandeln, das der (JSON Resume Schema) Struktur entspricht.

Regeln:
1. Extrahiere persönliche Informationen, Berufserfahrung, Ausbildung, Fähigkeiten, Projekte, Sprachen und Zertifikate.
2. Wenn du Links findest (LinkedIn, GitHub, Webseite), setze sie an die richtige Stelle.
3. Behalte die Sprache des Textes bei (wenn der Text auf Deutsch ist, extrahiere die Daten auf Deutsch).
4. Antworte **NUR** mit validem JSON-Code, ohne zusätzlichen Text oder Einleitungen.
5. Erforderliche Struktur:
   - basics: {{ name, email, phone, url, summary, location, profiles: [{{ network, url }}] }}
   - work: [{{ name, position, startDate, endDate, highlights: [] }}]
   - education: [{{ institution, area, studyType, startDate, endDate, courses: [], notes }}]
   - skills: [{{ name, keywords: [] }}]
   - projects: [{{ name, description, highlights: [], keywords: [], url }}]
   - certificates: [{{ name, issuer, date }}]
   - languages: [{{ language, fluency }}]

Zu analysierender Text:
---
{text}
---
"""

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
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            content = response.text.strip()
            
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        data = json.loads(content)
        return data
    except Exception as e:
        print(f"Fehler bei der KI-Analyse: {e}")
        return None

def generate_cover_letter_data(cv_data: dict, job_description: str, api_key: str, provider: str = 'gemini') -> Optional[dict]:
    prompt = f"""
Act as a professional German Career Coach Expert and formal cover letter writer.

Your task is to write an "Anschreiben" (Cover Letter) in German or the language of the job advertisement, based on the provided data.

⚠️ Strictly follow these rules:

1. Structure:
- Follow a modern professional German cover letter structure (without the full DIN 5008 header formatting).
- Salutation (Anrede): Use a specific name only if explicitly mentioned in the job description, otherwise use "Sehr geehrtes Recruiting-Team".
- First Paragraph (Motivation): Clearly explain why this specific company and this specific role. Do NOT start with "Hiermit bewerbe ich mich".
- Second Paragraph (Experience): Mention real practical experience with clear examples and technologies used.
- Third Paragraph (Skill Matching): Directly connect the candidate's skills to the job requirements and demonstrate the ability to learn quickly.
- Last Paragraph (Closing): Mention availability and express a strong desire for an interview.
- Mention salary expectations ONLY if explicitly requested in the job description.
- Close with "Mit freundlichen Grüßen".
- Do not repeat the same idea across different paragraphs.

2. Content & Tone:
- Use formal and professional German language (B2-C1 level).
- Do not use generic phrases or clichés.
- Use ONLY information provided in the CV and the Job Description (Do NOT invent or hallucinate data).
- Focus on achievements and business impact rather than just listing tasks.
- Use a clear, direct, and professional tone without filler words.

3. Customization & Optimization:
- Directly link each paragraph to the job requirements.
- Naturally integrate keywords from the job advertisement.
- Optimize the text to be ATS-friendly.
- Use short, clear paragraphs without bullet points.
Gebe die Antwort NUR im folgenden JSON-Format aus:

{{
  "recipient": {{
    "company": "Firmenname",
    "contact_person": "Ansprechpartner laut Job-Beschreibung (oder 'Recruiting-Team')",
    "address": "Adresse",
    "postal_code": "PLZ",
    "city": "Stadt"
  }},
  "location": "Wohnort des Kandidaten (aus CV)",
  "subject": "Betreff: Bewerbung als [Position]",
  "salutation": "Sehr geehrte(r)...",
  "paragraphs": [
    "Einleitung...",
    "Hauptteil 1...",
    "Hauptteil 2...",
    "Schluss..."
  ],
  "closing": "Mit freundlichen Grüßen"
}}

Lebenslauf Daten (CV):
{json.dumps(cv_data, ensure_ascii=False)}

Job-Beschreibung:
{job_description}
"""
    try:
        if provider == 'openai':
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Du bist ein Karrierespezialist. Antworte NUR im validen JSON-Format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro-latest') # using pro for better text generation if available, or just flash
            response = model.generate_content(prompt)
            content = response.text.strip()
            
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        data = json.loads(content)
        return data
    except Exception as e:
        print(f"Fehler bei der KI-Analyse des Anschreibens: {e}")
        return None

def rate_cv(cv_text: str, api_key: str, provider: str = 'openai') -> Optional[str]:
    prompt = f"""
Du bist ein erfahrener HR-Experte und Recruiter in Deutschland.
Bewerte den folgenden Lebenslauf-Text basierend auf seiner aktuellen Struktur, Klarheit und Eignung für moderne Bewerbungen (ATS).
Bitte sei konstruktiv, gib dem CV eine Punktzahl von 1 bis 10 und zähle 2-3 Stärken sowie 2-3 Verbesserungsvorschläge auf.
Reagiere kurz und bündig (als einfacher Text).

Lebenslauf-Text:
{cv_text}
"""
    try:
        if provider == 'openai':
            from openai import OpenAI
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
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text.strip()
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