# KI-Lebenslauf-Generator (AI CV Generator) 🚀

Ein professionelles Python-Tool zur automatischen Erstellung perfekt formatierter Lebensläufe im `.docx`-Format. Das Tool kann entweder strukturierte JSON-Daten verwenden oder mittels KI (Google Gemini) unstrukturierten Rohtext direkt in einen formatierten Lebenslauf umwandeln.

## 📌 Funktionen
- **KI-Textanalyse:** Wandelt ungeordneten Text (z. B. aus LinkedIn-Profilen oder alten Dokumenten) automatisch in ein strukturiertes JSON-Format um.
- **Professionelle Formatierung:** Automatische Erstellung von Word-Dokumenten mit präziser Ausrichtung, anklickbaren Hyperlinks und sauberer Typografie (Calibri).
- **A4-Standard:** Optimiert für das europäische A4-Format mit korrekter Paginierung und Umbruchschutz für Absätze.
- **Datentrennung:** Klare Trennung zwischen Inhalten (`data.json`) und Design (`cv_generator.py`).

## ⚙️ Installation
Klonen Sie das Repository und installieren Sie die Abhängigkeiten:
```bash
git clone https://github.com/amjad-awad-allah/cvscript.git
cd cvscript
pip install -r requirements.txt
```

## 🚀 Nutzung

### 1. Verwendung des KI-Generators (Empfohlen)
Dieses Skript führt Sie durch den gesamten Prozess von der Textanalyse bis zur Word-Datei:

1. Erstellen Sie eine Datei namens `.env` im Hauptverzeichnis.
2. Fügen Sie Ihren Google Gemini API-Key hinzu:
   ```text
   GEMINI_API_KEY=Ihr_API_Key_Hier
   ```
3. Kopieren Sie Ihren Lebenslauf-Rohtext in die Datei `raw_cv.txt`.
4. Starten Sie den Prozess:
   ```bash
   python main.py
   ```

### 2. Manuelle Generierung aus JSON
Falls Sie die Daten bereits im JSON-Format vorliegen haben:
1. Bearbeiten Sie die Datei `data.json` nach Ihren Wünschen.
2. Starten Sie die Generierung:
   ```bash
   python cv_generator.py
   ```

### 3. Generierung des Anschreibens (Cover Letter)
Sie können nun auch ein professionelles Anschreiben im gleichen Stil erstellen:
- Bearbeiten Sie die `cover_letter.json` mit den Empfängerdaten und Textabsätzen.
- Der Generator übernimmt Ihre persönlichen Daten (Name, Adresse, Kontakt) automatisch aus der `data.json`.
- Führen Sie einfach die `main.py` aus und wählen Sie am Ende "j", um das Anschreiben zu generieren.

## 🧩 Projektstruktur
- `main.py`: Zentrales Skript für den Workflow (Text -> KI -> JSON -> Word).
- `text_analyzer.py`: Modul zur KI-gestützten Analyse mittels Gemini API.
- `cv_generator.py`: Modul zur Erstellung der Word-Datei (`.docx`).
- `data.json`: Die strukturierte Datenquelle im JSON-Resume-Format.
- `raw_cv.txt`: Eingabedatei für unstrukturierten Rohtext.

## 📄 Lizenz
MIT License
