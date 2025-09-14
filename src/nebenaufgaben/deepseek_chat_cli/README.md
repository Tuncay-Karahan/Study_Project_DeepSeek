# DeepSeek CLI (Ollama) – mit Spinner & Notebook-Support

<p style="font-size:17px">
Ein kleines <b>Terminal-Tool</b> und eine <b>Notebook-Utility</b>, um mit <b>DeepSeek-R1</b>
oder <b>DeepSeek-Math</b> über den lokalen Ollama-Server zu chatten.  
Während eine Antwort berechnet wird, zeigt ein <b>Spinner</b> im Terminal den Fortschritt an.  
Im Notebook kannst du die Funktion `get_model_response()` nutzen, um Prompts direkt 
in Python-Zellen abzusetzen (mit History).
</p>


## Features

- Wechsel zwischen **DeepSeek-R1 (32B)** und **DeepSeek-Math (7B)** per Kommentarzeile  
- Wahl zwischen **`/api/generate`** (Prompt-Modus) und **`/api/chat`** (Chat-Verlauf)  
- Spinner-Animation während DeepSeek arbeitet, die nach Fertigstellung **verschwindet**  
- Konfigurierbare Optionen (temperature, top_p, repeat_penalty, num_predict …)  
- Saubere Fehlerbehandlung, beenden mit `exit`, `quit`, `ende`, `bye`


## Voraussetzungen

- **Python 3.10+**
- Installierte Bibliothek:
  ```bash
  pip install requests
  ```
- **Ollama** lokal installiert und laufend:
  ```bash
  ollama serve
  ```
- Modell(e) geladen:
  ```bash
  ollama pull deepseek-r1:32b
  ollama pull t1c/deepseek-math-7b-rl:latest
  ```


## Nutzung

Starte das Skript im Terminal:

```bash
python deepseek_cli_flex.py
```

Beispiel:

```
DeepSeek CLI (Ollama)
Modus: /api/chat
Modell: deepseek-r1:32b
Mit 'exit', 'quit', 'ende' oder 'bye' beenden.

> Was ist die Ableitung von x²?
DeepSeek arbeitet… /

Antwort:
Die Ableitung von x² nach x ist 2x.
```


## Umschalten zwischen Modellen

Im Code:

```python
MODEL = DEEPSEEK_MODEL
# MODEL = MATH_MODEL
```

- Aktive Zeile ohne `#` → Modell wird genutzt  
- Andere Zeile auskommentieren


## Umschalten zwischen Endpunkten

Im Code:

```python
OLLAMA_URL = "http://localhost:11434/api/generate"
# OLLAMA_URL = "http://localhost:11434/api/chat"
```

- `/generate`: einfacher Prompt → direkte Antwort  
- `/chat`: Chat-Verlauf mit History (Nachrichten werden gespeichert)

---

## Konfigurierbare Parameter

Im Abschnitt `OPTIONS` kannst du das Verhalten anpassen:

```python
OPTIONS = {
    "temperature": 0.1,      # Kreativität (0.0 = strikt, 1.0 = kreativ)
    "top_p": 0.9,            # Nucleus Sampling
    "repeat_penalty": 1.1,   # Strafe für Wiederholungen (>1.0 = strenger)
    "num_predict": 320,      # maximale Tokens pro Antwort
    "format": "json",        # Output-Format (sofern Modell es beachtet)
    "stop": ["```"]          # Stop-Sequenzen
}
```


## Nutzung im Jupyter Notebook

Importiere die Wrapper-Funktion `get_model_response` aus dem Skript.  
Damit kannst du Prompts absetzen und eine History aufbauen:

```python
# Importiere die Funktion aus dem promt_Skript Skript
from deepseek_cli_flex import get_model_response

# History am Anfang einmalig anlegen
history = []

# Hilfsfunktion für Jupyter Notebook
def ask(prompt):
    global history
    text, history = get_model_response(prompt, history=history)
    return text

# Erster Prompt
ask("Was ist 324 + 478?")

# Zweiter Prompt (nutzt History)
ask("Gebe mir die zahl pi auf 25 nachkommastellen")


## Ordnerstruktur

Empfohlene Ablage:

```
src/
└─ nebenaufgaben/
   └─ deepseek_chat_cli/
      ├─ deepseek_cli_flex.py
      └─ README.md
```

---

## Beenden

Eingabe einer der folgenden Kommandos:
- `exit`  
- `quit`  
- `ende`  
- `bye`

---
