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
    
    # 1. API Key abfragen, falls nicht gesetzt
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Fehler: Bitte setzen Sie zuerst Ihren GEMINI_API_KEY.")
        print("Beispiel (Windows Powershell): $env:GEMINI_API_KEY = \"Ihr_Schlüssel_Hier\"")
        print("Beispiel (Linux/Mac): export GEMINI_API_KEY=\"Ihr_Schlüssel_Hier\"")
        return

    # 2. Daten aus Rohtext extrahieren
    if not os.path.exists(raw_file):
        print(f"Fehler: {raw_file} wurde nicht gefunden. Bitte erstellen Sie die Datei und fügen Sie Ihren Lebenslauftext ein.")
        return
        
    print(f"Lese {raw_file}...")
    with open(raw_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    print("--- [ Schritt 1: KI-Textanalyse ] ---")
    extracted_data = text_analyzer.analyze_cv_text(raw_text, api_key)
    
    if not extracted_data:
        print("Fehler: Die Daten konnten nicht korrekt extrahiert werden.")
        return

    # 3. Bestätigungsschritt
    print("KI hat die Daten erfolgreich extrahiert.")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
    print(f"Daten wurden in {json_file} gespeichert.")
    
    confirm = input("Möchten Sie das Word-Dokument jetzt generieren? (j/n): ")
    if confirm.lower() != 'j':
        print("Vorgang abgebrochen. Sie können data.json manuell bearbeiten und den Generator später ausführen.")
        return

    # 4. DOCX generieren
    print("--- [ Schritt 2: Generierung der Word-Datei ] ---")
    cv_generator.generate_cv(json_file, output_docx)

if __name__ == "__main__":
    main()
