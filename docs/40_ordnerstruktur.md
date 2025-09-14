# Arbeitsbereich & Ordnerstruktur

Die Skripte **müssen im selben Ordner** liegen wie die Klausuren (`SS_*` / `WS_*`).  
Das **1. Skript** erzeugt `mathe_2_klausur_<SEM>/`, die Skripte **2 & 3** schreiben in **denselben** Ordner weiter.

Siehe ausführliche Anleitung: `klausuren_workspace/README.md`.

## Kurzüberblick (Beispiel)

```
klausuren_workspace/
├─ 1_latex_to_json.py
├─ 2_send_to_models.py
├─ 3_compare_and_score.py
├─ SS_24/
│  ├─ SS_24/
│  │  ├─ M2_IT/
│  │  │  └─m2_it_ss_24_dgl_erster_ordnung.tex
│  │  │  └─m2_it_ss_24_dgl_system.tex
│  │  │  └─m2_it_ss_24_differenzengleichung.tex
│  │  │  └─m2_it_ss_24_kurzaufgaben.tex
│  │  └─ M2_SWB_TIB/
│  │  │  └─m2_swb_tib_ss_24.tex                ← Hauptdatei (enthält \input{...})
│  │  │  └─m2_swb_tib_ss_24_fourier-reihen.tex
│  │  │  └─m2_swb_tib_ss_24_potenzreihen.tex
│  │  └─ M2_WKB/
├─ WS_24/
│  ├─ WS_24/
│  │  ├─ M2_IT/
│  │  ├─ M2_SWB_TIB/
│  │  │  └─ m2_swb_tib_ws_24.tex               ← (analog)
│  │  └─ M2_WKB/
│
├─ mathe_2_klausur_SS_24/                      ← Output von Script 1 (und dann 2 & 3)
│  ├─ mathe_2_klausur_SS_24.tex
│  ├─ mathe_2_klausur_SS_24.json
│  ├─ mathe_2_klausur_SS_24_antworten_openai.json
│  ├─ mathe_2_klausur_SS_24_antworten_deepseek.json
│  ├─ mathe_2_klausur_SS_24_antworten_math.json
│  ├─ mathe_2_klausur_SS_24_antworten_summary.json
│  └─ mathe_2_klausur_SS_24_bewertung_ai.json
│
└─ mathe_2_klausur_WS_24/                      ← weiterer Output-Ordner für WS_24
   ├─ mathe_2_klausur_WS_24.tex
   ├─ mathe_2_klausur_WS_24.json
   ├─ mathe_2_klausur_WS_24_antworten_openai.json
   ├─ mathe_2_klausur_WS_24_antworten_deepseek.json
   ├─ mathe_2_klausur_WS_24_antworten_math.json
   ├─ mathe_2_klausur_WS_24_antworten_summary.json
   └─ mathe_2_klausur_WS_24_bewertung_ai.json
```