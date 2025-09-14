# Arbeitsbereich: Klausuren + Skripte

Dieses Verzeichnis enthält die drei Hauptskripte **und die Klausuren-Ordner** (z. B. `SS_24/`, `WS_24/`).  
Die Skripte greifen direkt auf diese Ordner zu und erzeugen pro Semester einen eigenen Output-Ordner.

---

## 1. Eingabestruktur

Jede Klausur liegt in einem Semester-Ordner mit **fixer Struktur**:

```
SS_24/
├─ M2_IT/
│  ├─ m2_it_ss_24_dgl_erster_ordnung.tex
│  ├─ m2_it_ss_24_dgl_system.tex
│  ├─ m2_it_ss_24_differenzengleichung.tex
│  └─ m2_it_ss_24_kurzaufgaben.tex
└─ M2_SWB_TIB/
   ├─ m2_swb_tib_ss_24.tex            ← Hauptdatei (enthält \input{...})
   ├─ m2_swb_tib_ss_24_fourier-reihen.tex
   └─ m2_swb_tib_ss_24_potenzreihen.tex
```

- Die **Hauptdatei** ist immer `m2_swb_tib_<sem>.tex`.  
- Sie bindet weitere TeX-Dateien mit `\input{...}` ein.  
- Optional gibt es `M2_WKB/`.

---

## 2. Position der Skripte

Die drei Skripte liegen **im selben Verzeichnis** wie die Klausurordner:

```
klausuren_workspace/
├─ 1_latex_to_json.py
├─ 2_send_to_models.py
├─ 3_compare_and_score.py
├─ SS_24/
└─ WS_24/
```

---

## 3. Output-Ordner

Nach Ausführung von `1_latex_to_json.py` wird automatisch ein Ordner erzeugt:

```
mathe_2_klausur_SS_24/
├─ mathe_2_klausur_SS_24.tex
├─ mathe_2_klausur_SS_24.json
```

Die Skripte 2 und 3 ergänzen weitere Dateien:

```
mathe_2_klausur_SS_24/
├─ mathe_2_klausur_SS_24_antworten_openai.json
├─ mathe_2_klausur_SS_24_antworten_deepseek.json
├─ mathe_2_klausur_SS_24_antworten_math.json
├─ mathe_2_klausur_SS_24_antworten_summary.json
└─ mathe_2_klausur_SS_24_bewertung_ai.json
```

---

## 4. Ausführung

Im Verzeichnis `klausuren_workspace/`:

```bash
python 1_latex_to_json.py
python 2_send_to_models.py
python 3_compare_and_score.py
```

---

## 5. Hinweise

- Pro Semester entsteht **ein eigener Output-Ordner**.  
- Echte Klausuren ggf. **nicht ins öffentliche Git-Repo committen** → stattdessen nur Beispielklausuren hochladen.  
- Falls Ordner leer bleiben sollen (z. B. `data/raw/`), kann man `.gitkeep` nutzen, damit Git die Ordner mitführt.
