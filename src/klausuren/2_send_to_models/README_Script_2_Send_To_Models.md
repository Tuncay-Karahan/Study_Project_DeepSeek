# 2) Aufgaben an Modelle senden → Antworten speichern
**Script:** `2_send_to_models.py`  
**Stand:** 2025-09-13

## Zweck
Lädt die aus Script 1 erzeugte JSON-Klausur und lässt **alle Aufgaben** von drei Modellen beantworten:
- OpenAI (`gpt-5-mini`)
- DeepSeek-R1 (über **Ollama**)
- DeepSeek-Math (über **Ollama**)

Alle Antworten werden pro Aufgabe gesammelt und in drei Dateien gespeichert.

## Ein-/Ausgaben
- **Input:** `mathe_2_klausur_<Semester>/<...>.json` (aus Script 1)
- **Output (im gleichen Ordner):**
  - `<basename>_antworten_openai.json`
  - `<basename>_antworten_deepseek.json`
  - `<basename>_antworten_math.json`
  - `<basename>_antworten_summary.json` (Zeitmessungen)

## Voraussetzungen
- `OPENAI_API_KEY` gesetzt
- **Ollama** lokal installiert + Modelle `deepseek-r1:32b` und `t1c/deepseek-math-7b-rl` verfügbar
- Python-Pakete: `openai`, `ollama`

## Aufruf
```bash
python "2.5 JSON_Aufgabe_an_Openai_Deepseek_und_DeepMath_senden .py"
# 1) mathe_2_klausur_* Ordner wählen
# 2) JSON-Datei innerhalb des Ordners wählen
# 3) Script erzeugt die drei *_antworten_*.json + Summary
```

## Details
- **Prompting:** sehr strenge System-Prompts, die **EXAKT** `{"antwort":"..."}` verlangen (keine Erklärungen).  
- **Few-Shots:** liefern Beispiele für Format & Mathematik.  
- **Ollama-Optionen (DeepSeek-R1):** konservative Parameter (`temperature=0.1`, `top_p=0.9`, `repeat_penalty=1.1`, `num_predict≈320`).  
- **Parser:** extrahiert robust das letzte gültige `{"antwort":"..."}`-Objekt (Trimmung, Fallback bei verschachteltem JSON).  
- **Timing:** misst Modell-Laufzeiten pro Phase und schreibt eine kompakte Summary.

## Typische Stolpersteine
- Ollama nicht gestartet oder Modell nicht vorhanden → DeepSeek-Phasen schlagen fehl.
- Antworten enthalten kein valides JSON → Parser greift (prüfe Ergebnisse).
- `OLLAMA_URL` ist aktuell im Code auskommentiert; i. d. R. Standard-Endpoint von Ollama wird genutzt.

## Beispiel-Workflow
1. `mathe_2_klausur_WS_24.json` auswählen.  
2. JSON-Datei die Skript 1 erstellt hat innerhalb des Ordners wählen
3. Danach findest du je drei Antwortdateien (OpenAI/DeepSeek/Math) plus eine Summary mit Zeiten.  
4. Diese Dateien sind der **Input** für Script 3 (Vergleich).

