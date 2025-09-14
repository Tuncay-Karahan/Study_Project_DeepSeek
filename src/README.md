# src

In diesem Ordner liegen alle **Skripte** und **Nebenaufgaben** des Projekts.  
Er dient als Arbeitsbereich für die Entwicklung und Tests.

---

## Struktur

- **Hauptskripte**  
  Zentrale Skripte, die für die Verarbeitung der Klausuren benötigt werden  
  (z. B. `1_latex_to_json.py`, `2_send_to_models.py`, `3_compare_and_score.py`).

- **nebenaufgaben/**  
  Unterordner für zusätzliche Tools und Experimente:  
  - `deepseek_chat_cli/` → Terminal-Tool + Notebook-Wrapper zum Chatten mit DeepSeek über Ollama.  
  - `deepseek_klausurberechnung/` → Skript zum Durchrechnen einzelner Klausuren und Export nach Excel.  
  - `open-webui/` → Anleitung & Docker-Setup für Open WebUI.  

---

## Hinweise

- **Alle Hauptskripte** erwarten, dass sie im selben Ordner wie die Klausuren (`SS_*` / `WS_*`) liegen.  
- Die Unterordner bringen jeweils eine eigene `README.md` mit – bitte dort nachschauen für Details.  
