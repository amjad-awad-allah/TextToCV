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
أريدك أن تتصرف كخبير توظيف ألماني محترف (German Career Coach Expert) ومحرر خطابات رسمي.
مهمتك هي كتابة "Anschreiben" (خطاب تغطية) باللغة الألمانية أو لغة الإعلان الوظيفي بناءً على البيانات التي سأزودك بها.

⚠️ اتبع القواعد الصارمة التالية لضمان الجودة:

1. الهيكلية (Structure):
   - يجب أن تتبع الهيكلية الرسمية للخطابات الألمانية (DIN 5008).
   - الترويسة (Header): استخرج بيانات الشركة للحقول أدناه.
   - التحية (Anrede): حاول إيجاد اسم شخص محدد. إذا لم يوجد، استخدم "Sehr geehrtes Recruiting-Team" وتجنب "Sehr geehrte Damen und Herren" قدر الإمكان.
   - المقدمة (Einleitung): لا تبدأ بـ "Hiermit bewerbe ich mich". ابدأ بجملة جاذبة تظهر شغفي بالشركة أو المنتج.
   - الجسم (Hauptteil): اربط مهاراتي مباشرة بمتطلبات الوظيفة. استخدم أمثلة ملموسة (أرقام، مشاريع، تقنيات) حصراً من سيرتي ولا تخترع شيئاً.
   - الخاتمة (Schluss): ذكر تاريخ البدء، والراتب المتوقع (إذا طُلب). طلب مقابلة بثقة.
   - التوقيع (Grußformel): "Mit freundlichen Grüßen".

2. النبرة والأسلوب (Tone & Style):
   - اللغة: رسمية (Sie-Form) ولكن بحماس وحيوية (Modern Business German). توافق مع لغة الإعلان الوظيفي.
   - تجنب الكلمات الرنانة الفارغة (مثل: "belastbar", "teamfähig" دون دليل). استبدلها بأفعال وإنجازات.
   - الطول: لا يتجاوز صفحة واحدة (حوالي 250-350 كلمة).
   - تجنب الأخطاء القواعدية والإملائية تمامًا.

3. التخصيص (Customization):
   - اذكر اسم الشركة ورؤيتها (Vision) بوضوح في المقدمة.
   - إذا كانت هناك فجوة في المهارات بين سيرتي والوظيفة، اذكر أن مهاراتي قابلة للنقل (Transferable Skills) وأنني أتعلم بسرعة.
   - استخدم كلمات مفتاحية من وصف الوظيفة (Keywords) لتحسين القراءة الآلية (ATS).

4. التنسيق (Formatting):
   - استخدم فقرات قصيرة وواضحة (في مصفوفة paragraphs).
   - لا تستخدم نقاطًا (Bullet points) كثيرة داخل النص الرئيسي.

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