import os
import json
import google.generativeai as genai
from typing import Optional

def analyze_cv_text(text: str, api_key: str) -> Optional[dict]:
    """
    Verwendet die Gemini API, um CV-Daten aus Rohtext in das JSON-Resume-Format zu extrahieren.
    """
    genai.configure(api_key=api_key)
    
    # Modell konfigurieren
    model = genai.GenerativeModel('gemini-1.5-flash')
    
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

if __name__ == "__main__":
    # Test-Block
    KEY = os.environ.get("GEMINI_API_KEY")
    if not KEY:
        print("Bitte setzen Sie die Umgebungsvariable GEMINI_API_KEY.")
    else:
        if os.path.exists("raw_cv.txt"):
            with open("raw_cv.txt", "r", encoding="utf-8") as f:
                raw_text = f.read()
            
            print("Analysiere Text...")
            result = analyze_cv_text(raw_text, KEY)
            if result:
                with open("data_new.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print("Daten erfolgreich nach data_new.json extrahiert.")
        else:
            print("raw_cv.txt nicht gefunden.")