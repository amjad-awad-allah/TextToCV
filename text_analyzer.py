import os
import json
import google.generativeai as genai
from openai import OpenAI
from typing import Optional
import time
import copy

def analyze_cv_text(text: str, api_key: str, provider: str = 'gemini', target_language: str = 'German', custom_improvements: list = None) -> Optional[dict]:
    """
    Verwendet die Gemini API oder OpenAI API, um CV-Daten aus Rohtext in das JSON-Resume-Format zu extrahieren.
    """
    lang_code = "de" if "german" in target_language.lower() or "deutsch" in target_language.lower() else "en"
    
    extra_rule = ""
    if custom_improvements and len(custom_improvements) > 0:
        improvements_str = "\n".join([f"- {imp}" for imp in custom_improvements])
        extra_rule = f"\n\n*** CRITICAL INSTRUCTION (IMPROVEMENTS) ***\nDer Benutzer hat folgende Schwächen in seinem ursprünglichen Text identifiziert. Du MUSST diese Schwächen beim Extrahieren aktiv ausbessern und die Formulierungen professionell umschreiben:\n{improvements_str}\n**************************\n"

    prompt = f"""
Du bist ein erstklassiger Executive CV Writer, HR-Experte und professioneller Copywriter.
Deine Aufgabe ist es, den unten stehenden Text nicht nur zu extrahieren, sondern auf ein absolutes Premium-Niveau zu HEBEN (Upskilling in der Formulierung, ohne Fakten zu erfinden), und in ein präzises, FEHLERFREIES JSON-Format umzuwandeln.

WICHTIGE REGELN FÜR PREMIUM-QUALITÄT:
1. STARTER HOOK (basics.summary): Schreibe einen extrem starken, packenden "Professional Hook" (2-3 Sätze). Verkaufe den Kandidaten! Nenne die Kernkompetenz, die Jahre an Erfahrung und den einzigartigen Mehrwert. Keine langweiligen Standardfloskeln.
2. UPLEVELING DER ERFAHRUNG (work.highlights): Die Tätigkeiten müssen auf hohem Niveau klingen. Nutze starke Action-Verben (z.B. "Entwickelte", "Leitete", "Optimierte"). Betone den Business-Impact und echte Erfolge. Lass die Erfahrung NICHT juniorig oder wie eine einfache To-Do-Liste klingen.
3. KLARE, LESBARE SKILLS (skills): Gruppiere technische Fähigkeiten logisch (z.B. nach "Frontend", "Backend", "Tools", "Methoden" in `name`). Die `keywords` dürfen NUR kurze, saubere Begriffe sein (z.B. "React", "Python", "Docker"), KEINE ganzen Sätze!
4. KEINE REDUNDANZ: Vermeide jegliche Wiederholung. Integriere berufliche Projekte IMMER als 'highlights' in die jeweilige 'work' (Berufserfahrung) Station. Nutze das 'projects' Array NUR für reine Hobby-, Freelance- oder Open-Source-Projekte.
5. DATUMSFORMAT: Das Format 'MM.YYYY' (z.B. 06.2026) ist absolut korrekt. Übernimm diese Daten exakt so.

TECHNISCHE REGELN:
6. Die Ausgabesprache MUSS streng in der Zielsprache ({target_language}) sein.
7. Antworte **NUR** mit validem JSON-Code. Keine Trailing-Commas! Der Schlüssel "language" muss genau "{lang_code}" lauten.
8. Erforderliche JSON-Struktur:
   - language: "{lang_code}" 
   - basics: {{ name, email, phone, url, summary, location, profiles: [{{ network, url }}] }}
   - work: [{{ name, position, startDate, endDate, highlights: [] }}]
   - education: [{{ institution, area, studyType, startDate, endDate, courses: [], notes }}]
   - skills: [{{ name, keywords: [] }}]
   - projects: [{{ name, description, highlights: [], keywords: [], url }}]
   - certificates: [{{ name, issuer, date }}]
   - languages: [{{ language, fluency }}]
9. GRAMMATIK: C2-Level Native Speaker Niveau. Makellos, professionell.{extra_rule}

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
                        {"role": "system", "content": "Du bist ein C2-Level HR Copywriter und Daten-Extraktor. Antworte NUR mit validem JSON und fixiere alle Sprachfehler."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                content = response.choices[0].message.content.strip()
            else:
                genai.configure(api_key=api_key)
                try:
                    # Optimized for 2026: Using Gemini 2.5 Flash for fast CV extraction
                    model_name = 'gemini-2.5-flash'
                    model = genai.GenerativeModel(model_name, generation_config={"temperature": 0.3})
                    response = model.generate_content(prompt)
                except Exception:
                    # Fallback to the latest generic flash alias
                    try:
                        model = genai.GenerativeModel('gemini-flash-latest', generation_config={"temperature": 0.3})
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
    lang_code = "de" if "german" in target_language.lower() or "deutsch" in target_language.lower() else "en"
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

def update_cv_with_new_info(base_cv_text: str, new_info_text: str, api_key: str, provider: str = 'gemini', target_language: str = 'German') -> Optional[dict]:
    """
    Takes an existing CV and new information, and returns an updated JSON Resume.
    """
    lang_code = "de" if "german" in target_language.lower() or "deutsch" in target_language.lower() else "en"
    
    prompt = f"""
Du bist ein erstklassiger Executive CV Writer. 
Hier ist der aktuelle Lebenslauf eines Kandidaten (Base CV) und hier sind neue Informationen oder Aktualisierungen (New Info).

Deine Aufgabe:
1. Aktualisiere den Lebenslauf des Kandidaten, indem du die neuen Informationen sinnvoll integrierst.
2. Behalte die grundlegende Struktur و المهارات و الروابط من السيرة الذاتية الأساسية.
3. Verbessere die Formulierungen auf Premium-Niveau (C2 Native Speaker).
4. Sorge dafür, dass KEINE Redundanz entsteht.
5. Das Ergebnis muss ein valides JSON im JSON Resume Format sein.

WICHTIG:
- Nutze starke Action-Verben.
- Erstelle einen packenden Professional Hook am Anfang.
- Gruppiere Skills sauber.
- Sprache der Ausgabe: {target_language}.

Base CV Text:
{base_cv_text}

New Info Text:
{new_info_text}

JSON Struktur:
- language: "{lang_code}"
- basics: {{ name, email, phone, url, summary, location, profiles: [{{ network, url }}] }}
- work: [{{ name, position, startDate, endDate, highlights: [] }}]
- education: [{{ institution, area, studyType, startDate, endDate, notes }}]
- skills: [{{ name, keywords: [] }}]
- projects: [{{ name, description, highlights: [], keywords: [], url }}]
- certificates: [{{ name, issuer, date }}]
- languages: [{{ language, fluency }}]

Antworte NUR mit validem JSON.
"""
    for attempt in range(3):
        try:
            if provider == 'openai':
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an Executive CV Writer. Answer ONLY with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                content = response.choices[0].message.content.strip()
            else:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                content = response.text.strip()
            break
        except Exception as e:
            if attempt < 2: time.sleep(2); continue
            raise e
            
    if content.startswith("```json"): content = content[7:-3].strip()
    elif content.startswith("```"): content = content[3:-3].strip()
    return json.loads(content)

def rate_cv(cv_text: str, api_key: str, provider: str = 'openai', target_language: str = 'German') -> Optional[dict]:
    prompt = f"""
Du bist ein erfahrener, absolut professioneller HR-Experte und Recruiter in Deutschland.
Bewerte den folgenden Lebenslauf basierend auf seiner aktuellen Struktur, Klarheit und Eignung für moderne Bewerbungen (ATS).
Bitte sei absolut ehrlich und streng. Vermeide jegliche unnötigen Schmeicheleien oder Floskeln.
Achte GANZ BESONDERS auf grammatikalische und orthografische Fehler sowie auf den sprachlichen Ausdruck.
WICHTIG: Das Datumsformat 'MM.YYYY' (z.B. 06.2026) ist in Deutschland der absolute Standard. Markiere dieses Format unter keinen Umständen als Fehler oder Schwäche!
Bitte gib dem CV eine realistische Punktzahl von 1 bis 10. Zähle 2-3 echte Stärken sowie 2-3 konkrete Verbesserungsvorschläge auf (inklusive sprachlicher Mängel, falls vorhanden).

Antworte IMMER und AUSSCHLIESSLICH im folgenden JSON-Format, ohne zusätzlichen Text und ohne Markdown:
{{
  "score": "8/10",
  "strengths": ["Stärke 1", "Stärke 2"],
  "weaknesses": ["Schwäche 1", "Schwäche 2"]
}}
Bitte antworte immer auf {target_language}.

Lebenslauf-Text:
{cv_text}
"""
    try:
        content = ""
        for attempt in range(3):
            try:
                if provider == 'openai':
                    client = OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Du bist ein HR-Experte auf Deutsch. Antworte NUR mit JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    content = response.choices[0].message.content.strip()
                else:
                    genai.configure(api_key=api_key)
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        response = model.generate_content(prompt)
                    except Exception:
                        model = genai.GenerativeModel('gemini-flash-latest')
                        response = model.generate_content(prompt)
                    content = response.text.strip()
                break
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
            
        return json.loads(content)
    except Exception as e:
        print(f"Fehler bei der Bewertung: {e}")
        return {"score": "Fehler", "strengths": ["Keine Daten analysiert"], "weaknesses": ["Bitte überprüfe deinen API Key und versuche es erneut."]}

if __name__ == "__main__":
    openai_key = os.environ.get("OPENAI_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    KEY = openai_key or gemini_key
    provider = 'openai' if openai_key else 'gemini'
    if not KEY:
        print("Bitte setzen Sie die Umgebungsvariable OPENAI_API_KEY oder GEMINI_API_KEY.")