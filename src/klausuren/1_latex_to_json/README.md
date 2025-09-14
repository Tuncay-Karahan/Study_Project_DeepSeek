# 1) LaTeX → JSON Extraktion
**Script:** `1_latex_to_json.py`  
**Stand:** 2025-09-13

## Zweck
Liest eine Mathe-Klausur aus LaTeX-Dateien ein, führt sie zu einer Gesamtdarstellung zusammen und lässt ChatGPT ein konsistentes JSON mit Aufgaben, Lösungsschritten und *base_truth* erzeugen.

## Ein-/Ausgaben
- **Input (Ordnerstruktur):** Semester-Ordner `SS_*` oder `WS_*`, darin u. a. `M2_IT/`, `M2_SWB_TIB/` sowie eine Hauptdatei `M2_SWB_TIB/m2_swb_tib_<sem>.tex`.
- **Output (im neuen Ordner):** `mathe_2_klausur_<Semester>/`
  - `mathe_2_klausur_<Semester>.tex` (zusammengeführt)
  - `mathe_2_klausur_<Semester>.json` (Aufgabenliste im JSON, am Ende um *summary* erweitert)

## Voraussetzungen
- `OPENAI_API_KEY` als Umgebungsvariable
- Python-Pakete: `openai` (SDK v1), optional `tqdm` u. a. (siehe allgemeines `requirements.txt`)

## Aufruf
```bash
python "1_latex_to_json.py"
# 1) Semesterordner wählen (SS_*/WS_*)
# 2) Script erstellt Merge-*.tex und ruft ChatGPT an
# 3) Ergebnis liegt in mathe_2_klausur_<Semester>/*.json
```

## Details
- Findet Semester-Ordner per Prefix **SS_ / WS_** und lässt dich einen auswählen.  
- Ermittelt die Reihenfolge eingebundener Dateien über `\input{...}` in der Haupt-TeX.  
- Liest *.tex aus `M2_IT` und `M2_SWB_TIB`, sortiert sie, merged sie in eine Datei und ruft dann **ChatGPT (gpt-5-mini)** mit einem strengen Extraktions-Prompt auf (JSON-Felder: `id`, `frage`, `lösungsschritte`, `base_truth`).  
- Hängt eine Laufzeit-*summary* (Sekunden + human-readable) ans JSON an.

## Typische Stolpersteine
- `OPENAI_API_KEY` fehlt → Abbruch.
- Hauptdatei oder Ordner fehlen → vorher Struktur prüfen.
- Wenn das Modell kein valides JSON liefert, wird ein Fallback versucht; prüfe das Ergebnis vor der Weiterverarbeitung.

## Beispiel-Workflow
1. Semesterordner `WS_24` auswählen.  
2. Ergebnis liegt in `mathe_2_klausur_WS_24/mathe_2_klausur_WS_24.json`.  
3. Dieses JSON ist der **Input** für Script 2.

