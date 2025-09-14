# Nebenaufgaben

Dieser Ordner enthält **zusätzliche Tools, Experimente und Hilfsunterlagen**, die das Hauptprojekt unterstützen, aber **nicht** Teil der Kernpipeline sind.

---

## Inhalt (Unterordner)

- **deepseek_chat_cli/**
  - Kleines Terminal-Tool (mit Spinner) + Notebook-Wrapper, um lokal über **Ollama** mit **DeepSeek-R1 / DeepSeek-Math** zu chatten.
  - Enthält: `deepseek_cli_flex.py`, eigene `README.md`, Beispiele für `/api/chat`, History, Notebook-Helper.
  - Eignet sich besonders für schnelle Tests, Debugging oder kleine Interaktions-Sessions ohne die große Pipeline.
  - Im Notebook lässt sich das Modell komfortabel mit `ask()` oder `get_model_response()` ansprechen, inklusive Gesprächs-History.


- **deepseek_klausurberechnung/**
  - Modul zum **Durchrechnen einzelner Klausuren** und Sammeln der Ergebnisse in **Excel**.
  - Pipeline: PDF → (ChatGPT) JSON → DeepSeek → Bewertung → `.xlsx`.
  - Enthält: Skript, Installationshinweise, Bewertungslogik, Tipps.

- **open-webui/**
  - (Optional) Anleitung/Kommandos, um **Open WebUI** via Docker zu starten und mit **Ollama** zu verbinden.
  - CPU- und GPU-Varianten, Compose-Beispiele, Troubleshooting.



---

## Voraussetzungen (allgemein)

- **Python 3.10+**
- **Ollama** lokal (falls DeepSeek lokal genutzt wird):  
  ```bash
  ollama serve
