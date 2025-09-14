# Skripte: Klausur-Pipeline

Dieses Verzeichnis enthält die drei Hauptskripte, die nacheinander ausgeführt werden:

```
LaTeX-Klausur ──▶ 1_latex_to_json.py ──▶ JSON-Aufgaben
             ──▶ 2_send_to_models.py ──▶ Modellantworten
             ──▶ 3_compare_and_score.py ──▶ Bewertung
```

---

## 1. LaTeX → JSON
**Datei:** `1_latex_to_json.py`  
- Liest Klausuren aus LaTeX-Dateien.  
- Erzeugt `mathe_2_klausur_<SEM>.json` (Aufgaben + base_truth).

---

## 2. Aufgaben → Modelle
**Datei:** `2_send_to_models.py`  
- Schickt Aufgaben an:
  - OpenAI (gpt-5-mini)  
  - DeepSeek-R1  
  - DeepSeek-Math  
- Speichert Antworten in `<basename>_antworten_*.json`.

---

## 3. Antworten vergleichen
**Datei:** `3_compare_and_score.py`  
- Bewertet Antworten gegen base_truth.  
- Erstellt `<basename>_bewertung_ai.json`.

---

## Ausführung
Im Ordner `src/klausuren/`:

```bash
python 1_latex_to_json.py
python 2_send_to_models.py
python 3_compare_and_score.py
```
