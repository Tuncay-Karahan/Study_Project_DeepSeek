# DeepSeek – Klausur berechnen & Excel sammeln

Dieses Modul verarbeitet **einzelne Klausuren**:  
**PDF → (ChatGPT erzeugt) JSON → DeepSeek-Antworten & Bewertung → Excel-Report**.

Es ist unabhängig von der großen Pipeline nutzbar und eignet sich, wenn du schnell eine einzelne Klausur durchrechnen und die Ergebnisse **in Excel** sammeln willst.

---

## Inhalt
- [Voraussetzungen & Installation](#voraussetzungen--installation)
- [Ablauf im Überblick](#ablauf-im-überblick)
- [1) JSON-Datensatz aus der PDF erzeugen (mit ChatGPT)](#1-json-datensatz-aus-der-pdf-erzeugen-mit-chatgpt)
- [2) Skript starten (DeepSeek via Ollama)](#2-skript-starten-deepseek-via-ollama)
- [3) Output (Excel) & Spalten](#3-output-excel--spalten)
- [Bewertungslogik (wichtig)](#bewertungslogik-wichtig)
- [Tipps & Fehlerbehebung](#tipps--fehlerbehebung)

---

## Voraussetzungen & Installation

Python-Abhängigkeiten (CPU):
```bash
python -m venv .venv
# Windows:
# .venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

python -m pip install --upgrade pip
pip install requests pandas openpyxl sentence-transformers torch sympy
```

> **Hinweis:** `sentence-transformers` zieht i. d. R. automatisch ein passendes `torch` nach. Falls nicht, installieren wir es explizit (siehe oben).

Ollama + DeepSeek-Modell:
```bash
# Ollama installieren und Dienst starten (http://localhost:11434)
# Modelle laden:
ollama pull deepseek-r1:32b
```

Die Standard-URL im Skript ist:
```python
OLLAMA_URL = "http://localhost:11434/api/generate"
```

---

## Ablauf im Überblick

1. **PDF** (z. B. `m2_swb_tib_ss_23_kl.pdf`) **an ChatGPT hochladen** und daraus einen **JSON-Datensatz** erzeugen (Schema siehe unten).  
2. JSON-Datei (z. B. `m2_swb_tib_ss_23_kl.json`) in den Ordner des Skripts legen.  
3. **Skript starten** → es fragt: „Alle JSON-Dateien verarbeiten?“ oder einzelne auswählen.  
4. DeepSeek beantwortet jede Frage, das Skript bewertet die Antwort und erzeugt **Excel** (z. B. `m2_swb_tib_ss_23_kl.xlsx`).  
5. *(Optional)* Wenn du zusätzlich **OpenAI/ChatGPT-Antworten** haben willst, kannst du sie manuell ins Excel einfügen (eine eigene Spalte ergänzen).

---

## 1) JSON-Datensatz aus der PDF erzeugen (mit ChatGPT)

**Schritt A – PDF hochladen:**  
- Lade deine Klausur-PDF (`m2_swb_tib_ss_23_kl.pdf`) in ChatGPT hoch.

**Schritt B – Prompt für JSON-Erzeugung:**  
Kopiere diesen Prompt und passe den Klausurnamen an:

```
Erzeuge mir aus der hochgeladenen Klausur einen JSON-Datensatz mit folgender Struktur pro Aufgabe:

[
  {
    "id": "aufgabe_1a",
    "frage": "<Fragetext in Klartext (LaTeX bereinigt)>",
    "loesungsschritte": ["Schritt 1", "Schritt 2", "..."],
    "basetruth": "<Endergebnis oder Gleichung/Zuordnung in Klartext>",
    "keywords": ["Stichwort1", "Stichwort2"]
  },
  ...
]

Anforderungen:
- `frage` und `basetruth` bitte ohne LaTeX-Sonderbefehle; nutze Klartext (∫, √, ^, _).
- `id` als konsistente Kennung (z. B. aufgabe_1a, 1b, 1c ...).
- `loesungsschritte` in 2–6 prägnanten Bulletpoints.
- `keywords` mit 2–5 relevanten Begriffen (zur späteren Suche).
- Gib **nur** reines JSON zurück.
```

**Schritt C – Beispiel-Item:**

```json
{
  "id": "aufgabe_1a",
  "frage": "Ordnen Sie den Differentialgleichungen die Richtungsfelder zu: (A) y' = -y, (B) y' = -x, (C) y' = y², (D) y' = x².",
  "loesungsschritte": [
    "Vergleiche jede Gleichung mit typischem Richtungsfeldverlauf.",
    "(C) ist steigend bei positivem y, stärker als linear → passt zu y' = y².",
    "(B) ist achsensymmetrisch → passt zu y' = -x.",
    "(D) y' > 0 für alle x → wachsend → passt zu x².",
    "(A) y' < 0 für y > 0 → fallend → passt zu -y."
  ],
  "basetruth": "(C) → C, (B) → B, (D) → D, (A) → A",
  "keywords": ["Richtungsfeld", "Differentialgleichung"]
}
```

> **Validierung:** Stelle sicher, dass das JSON **valide** ist (keine Kommentare, alle Keys in Anführungszeichen). Speichere es z. B. als `m2_swb_tib_ss_23_kl.json`.

---

## 2) Skript starten (DeepSeek via Ollama)

Lege das Skript (z. B. `deepseek_klausur_to_excel.py`) und die JSON-Datei in **denselben Ordner**.  
*(Falls dein Skript noch `AI_compare_automatisch_wählbar_Latex-Cleaning_.py` heißt, funktioniert es genauso.)*

```bash
# Alle JSON-Dateien im Ordner verarbeiten:
python deepseek_klausur_to_excel.py

# Interaktiv: einzelne JSON auswählen
# (Das Skript listet vorhandene .json-Dateien und fragt nach Auswahl.)
```

Das Skript fragt:
- `Möchtest du alle JSON-Dateien im Verzeichnis verarbeiten? (j/n):`  
- Bei `n`: Auswahl per Nummern (z. B. `1,2,3`).

---

## 3) Output (Excel) & Spalten

Für `m2_swb_tib_ss_23_kl.json` entsteht automatisch:
```
m2_swb_tib_ss_23_kl.xlsx
```

**Spalten im Excel:**
- `ID` – Aufgabenkennung (z. B. `aufgabe_1a`)
- `Frage` – Fragetext in Klartext
- `Basetruth` – erwartetes Endergebnis / Gleichung / Zuordnung
- `Antwort DeepSeek (roh)` – Original-Output vom Modell
- `Antwort DeepSeek (final)` – extrahierte, bereinigte Endantwort
- `Ähnlichkeit` – Semantische Nähe zu `Basetruth` (0–1, drei Nachkommastellen)
- `Bewertung` – ✔️ korrekt / ➖ teilkorrekt / ❌ falsch

**Formatierungen:**
- Kopfzeile hellblau hinterlegt, fett
- Spaltenbreite automatisch (max. 100)
- Bewertung farbig:
  - ✔️ korrekt → grün
  - ➖ teilkorrekt → gelb
  - ❌ falsch → rot

---

## Bewertungslogik (wichtig)

Die Bewertung nutzt drei Ebenen:

1) **Symbolische Gleichheit (SymPy):**  
   - `pruefe_mathematische_gleichheit()` interpretiert beide Seiten und prüft *strikte* Gleichheit  
   - Wenn `True` → **✔️ korrekt (1.0)**

2) **Semantische Ähnlichkeit (Sentence-Transformers):**  
   - Modell: `paraphrase-MiniLM-L6-v2`  
   - `cos_sim`-Schwellen:
     - **> 0.85** → **✔️ korrekt**
     - **> 0.60** → **➖ teilkorrekt**
     - sonst → **❌ falsch**

3) **Schlüsselwörter (Fallback):**  
   - Wenn alle Wörter aus `basetruth` (lowercased, whitespace-gesplittet) in der Antwort vorkommen → **✔️ korrekt**

**Final-Answer-Extraktion:**  
- Entfernt `<think>...</think>`, `\boxed{...}`, LaTeX-Markup (`\\int`, `\\sqrt{}`, `\\frac{}` etc.)  
- Wandelt Dinge wie `\int_0^x` zu `∫₀ˣ` um (Unicode-Hoch-/Tiefstellungen)  
- Ziel: eine **klare Endantwort** ohne Rechenweg-Rauschen

---

## Tipps & Fehlerbehebung

- **Ollama läuft nicht?**  
  - `ollama serve` starten, `curl http://localhost:11434/api/tags` testen
- **Zu wenig VRAM / langsam?**  
  - Kleinere Modelle testen oder API-Modus (OpenAI) verwenden
- **JSON-Fehler?**  
  - Mit JSON-Validator prüfen (z. B. https://jsonlint.com/)  
  - Anführungszeichen um alle Keys, keine Kommentare `#`
- **Manuelle ChatGPT-Antworten ergänzen?**  
  - Du kannst eine zusätzliche Spalte im Excel anlegen: **„Antwort OpenAI (manuell)“**  
  - Fragen aus `Frage` in ChatGPT einfügen → Antwort kopieren → in Excel einfügen  
  - So kannst du DeepSeek vs. ChatGPT vergleichen

---

## Ordnerempfehlung

```text
src/
└─ nebenaufgaben/
   └─ deepseek_klausur_excel/
      ├─ deepseek_klausur_to_excel.py          # (oder dein bestehender Skriptname)
      ├─ m2_swb_tib_ss_23_kl.pdf               # Beispiel-PDF
      ├─ m2_swb_tib_ss_23_kl.json              # JSON-Datensatz
      ├─ m2_swb_tib_ss_23_kl.xlsx              # Ergebnis-Excel
      └─ README.md                              # diese Datei
```

