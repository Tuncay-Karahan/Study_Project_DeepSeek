import os
import re
import json
import time
import threading
import ollama
from openai import OpenAI

# ===============================================================
# Deepseek setup
# ===============================================================
#OLLAMA_URL = "http://localhost:11434/api/chat"
DEEPSEEK_MODEL = "deepseek-r1:32b"
MATH_MODEL = "t1c/deepseek-math-7b-rl"  
warmup_times = {}


# ===============================================================
# OpenAI setup
# ===============================================================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===============================================================
# Zeitformatierung
# ===============================================================
def _fmt_duration(seconds: float) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(int(m), 60)
    ms = int((seconds - int(seconds)) * 1000)
    if h:
        return f"{h}h {m}m {int(s)}s"
    if m:
        return f"{m}m {int(s)}s"
    return f"{int(s)}s {ms}ms"

# ===============================================================
# Prompt-Setup (streng & kurz)
# ===============================================================
SYSTEM_PROMPT = """
Du bist ein erfahrener Mathematik-Tutor.

AUSGABE:
- Antworte ausschließlich auf Deutsch.
- Gib NUR ein JSON-Objekt zurück, mit GENAU EINEM Feld: "antwort".
- KEINE Begründungen, KEINE Rechenschritte, KEIN Markdown, KEINE Überschriften.
- Beispiel: {"antwort":"y(1) ≈ -1.2397"}

REGELN:
- Nur das Endergebnis, max. 200 Zeichen.
- Kompakte Notation: e^{x}, √(·), (x,y), C1, C2, π, i.
- Mehrere Teilantworten mit "; " trennen.
- Falls unlösbar: {"antwort":"keine eindeutige Lösung aus den Angaben ableitbar"}.
"""

# ===============================================================
# Zusatz-Prompt speziell für DeepSeek (strengere Einschränkungen)
# ===============================================================
SYSTEM_PROMPT_DS_SUFFIX = """
ANTWORTFORMAT (SEHR WICHTIG):
Gib AUSSCHLIESSLICH ein einziges JSON-Objekt zurück, exakt:
{"antwort":"..."}
KEINE Erklärungen, KEINE Rechenschritte, KEIN Markdown/LaTeX, KEINE Backslashes.
Nur das Endergebnis als kurzer String (max. 200 Zeichen).

FORMATVORGABEN NACH AUFGABENTYP:
- Grenzwert: schreibe explizit z.B. lim_{x->0} f(x) = 1.
- Integralwert mit I: z.B. I ≈ 31/36 ≈ 0.8611111111
- DGL-Lösung: z.B. y(x) = C1 cos(2x) + C2 sin(2x) + (3/8) x sin(2x)
- System/Differenzengleichung: z.B. x_k = ...; y_k = ...
- Ja/Nein: z.B. Ja bzw. Nein
- Beginne deine Ausgabe IMMER unmittelbar mit {"antwort":" und schließe sie mit "}.
- Kein "Antwort:", keine Einleitung, kein Markdown.
"""
# ===============================================================
# Zusatz-Prompt speziell für Openai
# ===============================================================
SYSTEM_PROMPT_OPENAI_SUFFIX = """
ANTWORTFORMAT (WICHTIG):
Gib EXAKT ein JSON-Objekt {"antwort":"..."} ohne weitere Zeichen.
Wenn ein Grenzwert gefragt ist: schreibe lim_{...} ... = ....
Wenn ein Integral mit I gefragt ist: beginne mit I ≈ ....
Keine Erklärungen, nur das Ergebnis (<=200 Zeichen).
"""
# ===============================================================
# Few-Shot Beispiele für bessere Steuerung 
# ===============================================================
FEWSHOTS = [
    # Aufgabe 1a – DGL aus Fundamentallösung
    {"role":"user","content":"Finde DGL mit Fundamentallösung y(x)=e^{-2x}."},
    {"role":"assistant","content":'{"antwort":"y\'(x) = -2·y(x)"}'},

    # Aufgabe 1b – Resonanz
    {"role":"user","content":"y''+9y=r(x). Resonanz bei? Optionen: e^{-9x}, e^{9x}, 3cos(x), cos(3x)"},
    {"role":"assistant","content":'{"antwort":"cos(3x)"}'},

    # Aufgabe 2a – Linearität prüfen
    {"role":"user","content":"y'(x)·y(x)=sin(x). Linear?"},
    {"role":"assistant","content":'{"antwort":"Nichtlinear"}'},

    # Aufgabe 2b – Exakte Lösung AWP
    {"role":"user","content":"AWP y'·y=sin(x), y(0)=-1. Exakte Lösung?"},
    {"role":"assistant","content":'{"antwort":"y(x) = -√(3 − 2·cos(x))"}'},

    # Aufgabe 2c – Euler-Verfahren (h=1/2)
    {"role":"user","content":"Euler h=1/2, 2 Schritte, y(0)=-1, y\' = sin(x)/y. y(1)≈?"},
    {"role":"assistant","content":'{"antwort":"y(1) ≈ -1.2397"}'},

    # Aufgabe 3a – 2x2-DGL-System, allgemeine Lösung
    {"role":"user","content":"x\'=-2x+3y, y\'=10x-3y. Allgemeine Lösung?"},
    {"role":"assistant","content":'{"antwort":"(x,y)=C1 e^{−8t}(1,−2)+C2 e^{3t}(3,5)"}'},

    # Aufgabe 4a – Differenzengleichung, erste Werte
    {"role":"user","content":"20x_{k+1}-21x_k=-200, x0=100. Gib x1, x2."},
    {"role":"assistant","content":'{"antwort":"x1=95; x2=89.75"}'},

    # Aufgabe 6e – Fourier-Koeffizienten
    {"role":"user","content":"T=2; c_k=((−1)^k−1)/(2kπ)·i. Werte für c1, c2?"},
    {"role":"assistant","content":'{"antwort":"c1=−i/π; c2=0"}'},
]

# ===============================================================
# Parser: holt NUR das {"antwort":"..."} aus dem Modell-Output
#  - akzeptiert String/Zahl/Bool
#  - entpackt verschachtelte {"antwort":"{...}"}
#  - entfernt Zeilenumbrüche und kürzt hart auf max_len
# ===============================================================
def parse_last_json(text: str, max_len: int = 200):
    import json, re
    if not text:
        return None, "leer"

    # unsichtbare Zeichen weg
    text = text.strip().replace("\u200b", "").replace("\ufeff", "")

    def _sanitize(s: str) -> str:
        s = s.replace("\r", " ").replace("\n", " ").strip()
        s = re.sub(r"\s+", " ", s)
        return s if len(s) <= max_len else s[:max_len-1].rstrip() + "…"

    def _extract_from_obj(obj):
        if isinstance(obj, dict) and "antwort" in obj:
            val = obj["antwort"]
            # wenn String: evtl. verschachteltes JSON entpacken
            if isinstance(val, str):
                s = val.strip()
                if s.startswith("{") and s.endswith("}"):
                    try:
                        inner = json.loads(s)
                        if isinstance(inner, dict) and "antwort" in inner:
                            s = str(inner["antwort"]).strip()
                    except Exception:
                        pass
                return {"antwort": _sanitize(s)}, "ok"
            # sonst direkt zu String machen (Zahl/Bool/etc.)
            return {"antwort": _sanitize(str(val))}, "ok"
        return None, None

    # 1) Versuch: gesamter Text ist JSON
    try:
        obj = json.loads(text)
        d, status = _extract_from_obj(obj)
        if d: return d, status
        if isinstance(obj, list):
            for item in reversed(obj):
                d, status = _extract_from_obj(item)
                if d: return d, status
    except Exception:
        pass

    # 2) Fallback: letztes balanciertes {...} im Text
    spans, start, depth = [], -1, 0
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0: start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start != -1:
                    spans.append((start, i+1)); start = -1

    for a, b in reversed(spans):
        chunk = text[a:b]
        try:
            obj = json.loads(chunk)
            d, status = _extract_from_obj(obj)
            if d: return d, status
        except Exception:
            continue

    return None, "kein_valides_json_mit_antwort"

# ===============================================================
# Hilfsfunktion: Hauptaufgabe aus aufgabe_id extrahieren
# ===============================================================
def get_main_task(aufgabe_id: str) -> str:
    m = re.match(r"(aufgabe_\d+)", aufgabe_id)
    return m.group(1) if m else aufgabe_id

def warmup_deepseek_r1(model=DEEPSEEK_MODEL):
    try:
        t0 = time.perf_counter()
        ollama.chat(
            model=model,
            messages=[{"role": "user", "content": "ping"}],
            options={"num_predict": 1}
        )
        t1 = time.perf_counter()
        warmup_times["DeepSeek-R1"] = t1 - t0
    except Exception as e:
        warmup_times["DeepSeek-R1"] = f"Fehler: {e}"

# ===============================================================
# OpenAI: Frage an OpenAI senden
# ===============================================================
def ask_openai(question, aufgabe_id, model="gpt-5-mini"):
    try:
        messages = [
            {"role":"system","content": SYSTEM_PROMPT},
            *FEWSHOTS,
            {"role":"system","content": SYSTEM_PROMPT_OPENAI_SUFFIX},
            {"role":"system","content": 'Antworte EXAKT als {"antwort":"..."} ohne weitere Zeichen.'},
            {"role":"user","content": question.strip()}
        ]

        t0 = time.perf_counter()
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=1.0,   # has to be 1.0 in gpt-5-mini
            response_format={"type": "json_object"}, 
            # max_tokens=120,  # not allowed in gpt-5-mini
        )
        t1 = time.perf_counter()

        raw = response.choices[0].message.content.strip()
        parsed, _ = parse_last_json(raw)
        ans = parsed["antwort"] if parsed else raw
        print(f"[OpenAI] ist fertig mit der {aufgabe_id} • API-Dauer: {_fmt_duration(t1 - t0)}")

        return ans, (t1 - t0)
    except Exception as e:
        return f"[OpenAI Fehler] {e}", 0.0

# ===============================================================
# DeepSeek (Ollama): Frage an DeepSeek mit Verlauf senden
# ===============================================================
def ask_deepseek_with_history(question, aufgabe_id, history_per_main_task, model=DEEPSEEK_MODEL):
    main_task = get_main_task(aufgabe_id)

    if main_task not in history_per_main_task:
        history_per_main_task[main_task] = [
            {"role":"system","content": SYSTEM_PROMPT + SYSTEM_PROMPT_DS_SUFFIX},
            *FEWSHOTS
        ]
    messages = history_per_main_task[main_task].copy()
    # Zusatz-Schranke am Ende nochmal:
    messages.append({"role":"system","content": 'Gib EXAKT {"antwort":"..."} ohne weitere Zeichen.'})
    messages.append({"role":"user","content": question.strip()})

    try:
        t0 = time.perf_counter()
        response = ollama.chat(
            model=model,
            messages=messages,
            options={
                "temperature": 0.1,     # maximal konservativ
                "top_p": 0.9,
                "repeat_penalty": 1.1,
                "num_predict": 320,      # genug Platz -> kein Abbruch in der Rechnung
                "format": "json",
                "stop": ["```"]    # kappt Roman-Output
            },
            think=False
        )
        t1 = time.perf_counter()

        raw = response.message.content.strip()
        parsed, _ = parse_last_json(raw)
        ans = parsed["antwort"] if parsed else raw

        # Verlauf updaten (roh fürs Debug)
        history_per_main_task[main_task].append({"role":"user","content": question.strip()})
        history_per_main_task[main_task].append({"role":"assistant","content": raw})

        print(f"[DeepSeek] ist fertig mit der {aufgabe_id} • API-Dauer: {_fmt_duration(t1 - t0)}")

        return ans, (t1 - t0)
    except Exception as e:
        return f"[DeepSeek Fehler] {e}", 0.0

# ===============================================================
# DeepSeek-Math (Ollama): nur Frage, KEIN Prompt/Fewshots (liefert (antwort, dauer_s))
#  - kein Konsolen-Output (silent)
#  - falls kein {"antwort": "..."} im Rückgabestring, wird der Text in dieses Format gewrappt
# ===============================================================
def ask_deepseek_math(question, aufgabe_id, model=MATH_MODEL):
    try:
        t0 = time.perf_counter()
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": question.strip()}],
        )
        t1 = time.perf_counter()
        ans = response.message.content.strip()

        print(f"[DeepSeek-Math] ist fertig mit der {aufgabe_id} • API-Dauer: {_fmt_duration(t1 - t0)}")

        return ans, (t1 - t0)
    except Exception as e:
        return f"[DeepSeek-Math Fehler] {e}", 0.0

# ===============================================================
# Ordnerwahl (Klausur-Ordner suchen und auswählen)
# ===============================================================
def choose_klausur_folder():
    # Suche alle Ordner mit "mathe_2_klausur_*"
    folders = [d for d in os.listdir(".") if os.path.isdir(d) and d.startswith("mathe_2_klausur_")]
    if not folders:
        print("Keine Klausur-Ordner gefunden (mathe_2_klausur_*)")
        exit()

    print("Gefundene Klausur-Ordner:")
    for idx, f in enumerate(folders, start=1):
        print(f"{idx}: {f}")

    while True:
        choice = input(f"Bitte Nummer des zu bearbeitenden Ordners eingeben (1-{len(folders)}): ")
        if choice.isdigit() and 1 <= int(choice) <= len(folders):
            return folders[int(choice) - 1]
        print("Ungültige Eingabe, bitte erneut versuchen.")


# ===============================================================
# JSON-Datei innerhalb eines Ordners auswählen
# ===============================================================
def choose_json_file():
    # Listet alle JSON-Dateien im aktuellen Ordner auf und fragt den Nutzer nach Auswahl
    files = [f for f in os.listdir(selected_folder) if f.lower().endswith(".json")]
    
    if not files:
        print("Keine JSON-Dateien im aktuellen Ordner gefunden!")
        exit()

    print("Gefundene Klausuren:")
    for idx, f in enumerate(files, start=1):
        print(f"{idx}: {f}")

    while True:
        choice = input(f"Bitte Nummer der zu bearbeitenden Klausur eingeben (1-{len(files)}): ")
        if choice.isdigit() and 1 <= int(choice) <= len(files):
            chosen = files[int(choice) - 1]
            return os.path.join(selected_folder, chosen) 
        print("Ungültige Eingabe, bitte erneut versuchen.")

# ===============================================================
# Hauptfunktion: Fragen verarbeiten, Antworten speichern
# ===============================================================
def process_questions(input_json, openai_model="gpt-5-mini", deepseek_model=DEEPSEEK_MODEL, math_model=MATH_MODEL):
    t_global_start = time.perf_counter()
    
    # JSON laden
    with open(input_json, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    openai_results = []
    deepseek_results = []
    math_results = []

    # Zeiten
    openai_time_total = 0.0
    deepseek_time_total = 0.0
    math_time_total = 0.0

    # ========== PHASE 1: OpenAI rechnet die komplette Klausur ==========
    print("\n===== PHASE 1: OpenAI rechnet die komplette Klausur =====")
    for task in tasks:
        aufgabe_id = task.get("id", "unbekannt")
        frage = task.get("frage", "")
        if not frage:
            continue
        ans, dt = ask_openai(frage, aufgabe_id, model=openai_model)
        openai_time_total += dt
        if isinstance(ans, dict):
            openai_results.append({"id": aufgabe_id, "frage": frage, **ans})
        else:
            openai_results.append({"id": aufgabe_id, "frage": frage, "antwort": ans})
        print(f"  OpenAI gebraucht Zeit bis jetzt: {_fmt_duration(openai_time_total)}")
    
    # ========== PHASE 2: DeepSeek R1 rechnet die komplette Klausur ==========
    print("\n===== PHASE 2: DeepSeek R1 rechnet die komplette Klausur =====")
    if "DeepSeek-R1" in warmup_times:
        wt = warmup_times["DeepSeek-R1"]
        if isinstance(wt, float):
            print(f"[Warmup] DeepSeek-R1 brauchte {_fmt_duration(wt)} zum Laden")
        else:
            print(f"[Warmup] DeepSeek-R1 fehlgeschlagen: {wt}")

    history_deepseek = {}
    
    for task in tasks:
        aufgabe_id = task.get("id", "unbekannt")
        frage = task.get("frage", "")
        if not frage:
            continue
        ans, dt = ask_deepseek_with_history(frage, aufgabe_id, history_deepseek, model=deepseek_model)
        deepseek_time_total += dt
        if isinstance(ans, dict):
            deepseek_results.append({"id": aufgabe_id, "frage": frage, **ans})
        else:
            deepseek_results.append({"id": aufgabe_id, "frage": frage, "antwort": ans})
        print(f"  DeepSeek gebraucht Zeit bis jetzt: {_fmt_duration(deepseek_time_total)}")

    # ========== PHASE 3: DeepSeek-Math rechnet die komplette Klausur ==========
    print("\n===== PHASE 3: DeepSeek Mathe rechnet die komplette Klausur =====")
    # (kein Banner-Print, damit wirklich „den ganzen Output rausgenommen“ ist)
    for task in tasks:
        aufgabe_id = task.get("id", "unbekannt")
        frage = task.get("frage", "")
        if not frage:
            continue
        ans, dt = ask_deepseek_math(frage, aufgabe_id, model=math_model)
        math_time_total += dt
        math_results.append({"id": aufgabe_id, "frage": frage, "antwort": ans})
        print(f"  DeepSeek Mathe gebraucht Zeit bis jetzt: {_fmt_duration(math_time_total)}")

    # ===== Ergebnisse speichern =====
    basename = os.path.splitext(os.path.basename(input_json))[0]
    output_dir = os.path.dirname(input_json)

    openai_out = os.path.join(output_dir, f"{basename}_antworten_openai.json")
    deepseek_out = os.path.join(output_dir, f"{basename}_antworten_deepseek.json")
    math_out = os.path.join(output_dir, f"{basename}_antworten_math.json")
    summary_out = os.path.join(output_dir, f"{basename}_antworten_summary.json")

    # Warmup sauber extrahieren
    wt = warmup_times.get("DeepSeek-R1", 0.0)
    wt_sec = wt if isinstance(wt, float) else 0.0

    # DeepSeek inkl. Warmup (nur wenn Warmup-Zeit valide ist)
    deepseek_with_warmup_seconds = deepseek_time_total + wt_sec

    with open(openai_out, "w", encoding="utf-8") as f:
        json.dump(openai_results, f, indent=2, ensure_ascii=False)
    with open(deepseek_out, "w", encoding="utf-8") as f:
        json.dump(deepseek_results, f, indent=2, ensure_ascii=False)
    with open(math_out, "w", encoding="utf-8") as f:
        json.dump(math_results, f, indent=2, ensure_ascii=False)

    t_global_end = time.perf_counter()
    summary = {
        "klausur_name": basename,
        "timing": {
            "openai_seconds": round(openai_time_total, 3),
            "deepseek_seconds": round(deepseek_time_total, 3),
            "warmup_deepseek_r1_seconds":   round(wt_sec, 3),
            "deepseek_with_warmup_seconds": round(deepseek_with_warmup_seconds, 3),
            "math_seconds": round(math_time_total, 3),
            "total_runtime_seconds": round(t_global_end - t_global_start, 3),
            "total_runtime_with_warmup_seconds": round(t_global_end - t_global_start + deepseek_with_warmup_seconds, 3),

           
            
            "openai_human": _fmt_duration(openai_time_total),
            "deepseek_human": _fmt_duration(deepseek_time_total),
            "warmup_deepseek_r1_human":   _fmt_duration(wt_sec),
            "deepseek_with_warmup_human": _fmt_duration(deepseek_with_warmup_seconds),
            "math_human": _fmt_duration(math_time_total),
            "total_runtime_human": _fmt_duration(t_global_end - t_global_start),
            "total_runtime_with_warmup_human": _fmt_duration(t_global_end - t_global_start + deepseek_with_warmup_seconds),

        }
    }
    with open(summary_out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert in Ordner '{output_dir}':")
    print(f"  - {openai_out}")
    print(f"  - {deepseek_out}")
    print(f"  - {math_out}")
    print(f"  - {summary_out}")

    print("\nGesamtzeiten für Bewertung:")
    print(f"OpenAI-Bewertung: {_fmt_duration(openai_time_total)}")
    print(f"DeepSeek-Bewertung: {_fmt_duration(deepseek_time_total)}")
    print(f"Math-Bewertung: {_fmt_duration(math_time_total)}")
    print(f"\nGesamtlaufzeit: {_fmt_duration(t_global_end - t_global_start)}")

# ===============================================================
# Main: Einstiegspunkt
# ===============================================================
if __name__ == "__main__":
    threading.Thread(target=warmup_deepseek_r1, daemon=True).start()    
    selected_folder = choose_klausur_folder()
    selected_file = choose_json_file()
    process_questions(selected_file)