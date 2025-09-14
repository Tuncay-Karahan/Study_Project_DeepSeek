# Parameter-Übersicht

Dieses Projekt nutzt zwei Modellfamilien – **OpenAI (gpt-5-mini)** und **DeepSeek-R1 (32B)** – mit jeweils spezifischen Parametern.  
Hier eine Übersicht der aktuell eingesetzten Werte:

---

## OpenAI (`gpt-5-mini`)

- **model_openai**: `"gpt-5-mini"`  
  → Name des Modells, das über die OpenAI API angesprochen wird.

- **temperature**: `0.1`  
  → Wert zwischen **0.0–1.0**. Steuert die Kreativität/Zufälligkeit der Ausgabe.  
  - Niedrig (z. B. 0.1) = sehr deterministisch, wenig Varianz  
  - Hoch (z. B. 0.8) = kreativer, mehr Zufall  

- **response_format**: `{ "type": "json_object" }`  
  → Erzwingt, dass die Antwort als valides JSON zurückkommt.  
  - Hilfreich, wenn die Ausgabe direkt weiterverarbeitet werden soll.  

---

## DeepSeek-R1 (`deepseek-r1:32b`)

- **model_deepseek**: `"deepseek-r1:32b"`  
  → Name des lokal (Ollama) laufenden DeepSeek-Modells.

- **options.temperature**: `0.1`  
  → Wie oben: sehr niedrige Temperatur für **maximale Deterministik**.  

- **options.top_p**: `0.9`  
  → *Nucleus Sampling*: Modelle wählen Tokens nur aus den **Top-p-Wahrscheinlichkeiten**.  
  - Niedrig (z. B. 0.5) = konservativ, eng begrenzt  
  - Hoch (z. B. 0.9) = mehr Varianz, aber immer noch kontrolliert  

- **options.repeat_penalty**: `1.1`  
  → Bestraft Wiederholungen in der Ausgabe.  
  - Werte knapp über 1.0 verhindern „Endlosschleifen“ und redundante Texte.  

- **options.num_predict**: `320`  
  → Maximale Anzahl an Tokens, die das Modell in einer Antwort generieren darf.  
  - Muss groß genug gewählt sein, um die ganze Lösung aufzunehmen.  

- **options.format**: `"json"`  
  → Fordert explizit JSON-Ausgabe an.  

- **options.stop**: `["```"]`  
  → Definiert Stopp-Sequenzen, bei denen die Generierung abgebrochen wird.  
  - Hier: Wenn ein Markdown-Codeblock startet (` ``` `), wird die Ausgabe gekappt.  

- **think**: `false`  
  → Deaktiviert „Thinking mode“ (interne Ketten von Gedanken, die DeepSeek sonst mit ausgeben könnte).  
  - Ergebnis: **kürzere, saubere Antworten** ohne Zusatzgedanken.  

---

## Zusammenfassung

- Beide Modelle laufen **mit sehr konservativen Parametern** (`temperature = 0.1`) → Fokus auf Konsistenz & Nachvollziehbarkeit.  
- OpenAI gibt die Aufgaben direkt als JSON zurück.  
- DeepSeek erhält zusätzlich Kontrollparameter (`top_p`, `repeat_penalty`, `num_predict`, `stop`), um Ausgaben kurz, präzise und in JSON-Format zu halten.  
- Ziel: **reproduzierbare, auswertbare Antworten** ohne unnötigen „Romantext“.  
