# 3) Antworten mit Base-Truth vergleichen & bewerten
**Script:** `3_compare_and_score.py`  
**Stand:** 2025-09-13

## Zweck
Vergleicht die von den Modellen erzeugten Antworten mit der *base_truth* je Teilaufgabe und bewertet sie mit
**korrekt | teilweise korrekt | falsch**. Erst bewertet **OpenAI**, danach **DeepSeek-R1**. *DeepSeek‑Math bewertet nichts* (im Code auskommentiert). Ergebnisse werden aggregiert.

## Ein-/Ausgaben
- **Input (im gleichen Ordner):**
  - `<folder>.json` (Klausur + base_truth; aus Script 1)
  - `<folder>_antworten_openai.json` (aus Script 2)
  - `<folder>_antworten_deepseek.json` (aus Script 2)
  - `<folder>_antworten_math.json` (aus Script 2; wird von OpenAI mitbewertet)
- **Output:**
  - `<folder>_bewertung_ai.json` mit:
    - Einzelbewertungen (OpenAI/DeepSeek)
    - Punkte (1/0.5/0)
    - Gruppensummen nach Hauptaufgabe (`aufgabe_<nr>`)
    - Klausursumme (Prozente & Punkte)
    - Zeitmessungen

## Voraussetzungen
- `OPENAI_API_KEY` gesetzt
- **Ollama** mit `deepseek-r1:32b` für die DeepSeek-Bewerter-Phase
- Python-Pakete: `openai`, `ollama`

## Aufruf
```bash
python "3_compare_and_score.py"
# 1) mathe_2_klausur_* Ordner wählen
# 2) Script lädt Base/Antworten und produziert *_bewertung_ai.json
```

## Details
- **Bewertungs-Prompt (gleich für beide Bewerter):** strenger System-Prompt – **nur** eines der Wörter zurückgeben (keine Begründung).  
- **Punkte-Logik:** korrekt=1.0, teilweise=0.5, falsch=0.0.  
- **Gruppierung:** `aufgabe_12a` → `aufgabe_12`. Ausgabe zusätzlich pro Hauptaufgabe in Prozent.  
- **DeepSeek‑Math als Bewerter:** vollständig **auskommentiert** (nur OpenAI bewertet dessen Antworten).

## Typische Stolpersteine
- Eine der Dateien fehlt → Skript prüft und meldet.
- Modelle geben unzulässigen Text zurück → Regex/Punktelogik sind robust, aber prüfe Ausreißer.
- Unterschiedliche IDs zwischen Base und Antworten → nur übereinstimmende `id` werden verglichen.

