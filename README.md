# Studienprojekt – Automatisierter Leistungsvergleich von DeepSeek und ChatGPT bei mathematischen Prüfungsaufgaben

Dieses Projekt besteht aus drei Hauptskripten, die nacheinander ausgeführt werden. Sie bilden eine Pipeline:

```
LaTeX-Klausur ──▶ Script 1 ──▶ JSON-Aufgaben ──▶ Script 2 ──▶ Modellantworten ──▶ Script 3 ──▶ Bewertung
```

---

## 1) LaTeX → JSON extrahieren
**Script:** `src/klausuren/1_latex_to_json.py`  

**Zweck:**  
Liest eine Klausur aus LaTeX-Dateien ein, fügt sie zusammen und lässt ChatGPT ein **strukturiertes JSON** mit Aufgaben, Lösungsschritten und `base_truth` erzeugen.

**Input:** Semesterordner (`SS_*/WS_*` mit `M2_IT`, `M2_SWB_TIB`)  
**Output:**  
- `mathe_2_klausur_<Semester>.tex` (zusammengeführt)  
- `mathe_2_klausur_<Semester>.json` (Aufgabenliste + summary)

**Aufruf:**
```bash
python "src/klausuren/1_latex_to_json.py"
```

---

## 2) Aufgaben an Modelle senden
**Script:** `src/klausuren/2_send_to_models.py`  

**Zweck:**  
Schickt alle Aufgaben aus Script 1 an drei Modelle:
- OpenAI (`gpt-5-mini`)
- DeepSeek-R1 (Ollama)
- DeepSeek-Math (Ollama)

**Output:**  
- `<basename>_antworten_openai.json`  
- `<basename>_antworten_deepseek.json`  
- `<basename>_antworten_math.json`  
- `<basename>_antworten_summary.json` (Zeitmessungen)

**DeepSeek-R1-Parameter (empfohlen):**  
- `temperature = 0.1`  
- `top_p = 0.9`  
- `repeat_penalty = 1.1`  
- `num_predict ≈ 320`
- `format = json`
- `think = False`

**Aufruf:**
```bash
python "src/klausuren/2_send_to_models.py"
```

---

## 3) Antworten vergleichen & bewerten
**Script:** `src/klausuren/3_compare_and_score.py`  

**Zweck:**  
Vergleicht die Modellantworten gegen die `base_truth`.  

- Bewertung je Aufgabe: &nbsp;**korrekt | teilweise korrekt | falsch**  
- Punkte:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**korrekt = 1.0 |&nbsp;&nbsp; teilweise = 0.5  &nbsp;| falsch = 0.0**
- Gruppierung nach Hauptaufgabe (`aufgabe_1a` & `aufgabe_1b` & `aufgabe_1c` → `aufgabe_1`)  
- **DeepSeek-Math bewertet nicht** (auskommentiert; nur von OpenAI beurteilt)

**Output:**  
- `<basename>_bewertung_ai.json` (Einzelbewertungen, Punktsummen, Prozente, Zeitmessung)

**Aufruf:**
```bash
python "src/klausuren/3_compare_and_score.py"
```

---

## Datenablage (Klausuren)
- Für Reproduzierbarkeit reicht **eine Beispiel-Klausur** mit derselben Ordnerstruktur (z. B. `examples/WS_24_sample/…`).  
- Echte Klausuren mit Urheberrecht/Datenschutz lieber **lokal in `data/raw/`** (ist in `.gitignore`) oder in ein privates Repo/Git-LFS.

---

## Quickstart

```bash
# Virtuelle Umgebung anlegen
python -m venv .venv

# Aktivieren:
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# API-Key setzen (z. B. unter Linux/macOS)
export OPENAI_API_KEY="sk-..."

# Pipeline ausführen
python src/klausuren/1_latex_to_json.py
python src/klausuren/2_send_to_models.py
python src/klausuren/3_compare_and_score.py
```

---

## Ordnerübersicht

```
.
├─ README.md                # Haupteinstieg
├─ requirements.txt
├─ .env.example             # Platzhalter für Keys
├─ configs/
│  └─ default.json
├─ src/
│  ├─ klausuren/            # 3 Main-Skripte
│  └─ nebenaufgaben/        # kleinere Tools (z. B. OpenUI + Docker)
├─ data/
│  ├─ raw/                  # Original-Klausuren (lokal, nicht im Repo)
│  ├─ intermediate/
│  └─ results/
├─ docs/                    # Setup, Hardware, Parameter
├─ examples/                # Beispielklausuren & Outputs
└─ scripts/                 # Run-All-Skripte (Bash/PowerShell)
```

---

## Lizenz
MIT License – siehe [LICENSE](LICENSE)
