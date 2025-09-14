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
DEEPSEEK_MODEL = "deepseek-r1:32b"
# MATH_MODEL     = "t1c/deepseek-math-7b-rl"
warmup_times = {}  # {"DeepSeek-R1": float|str}

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
# Warmup (Hintergrund) für DeepSeek-R1
# ===============================================================
def warmup_deepseek_r1(model=DEEPSEEK_MODEL):
    try:
        t0 = time.perf_counter()
        # Minimaler Call, blockiert aber im Hintergrund-Thread, Hauptthread läuft weiter
        ollama.chat(
            model=model,
            messages=[{"role": "user", "content": "ping"}],
            options={"num_predict": 1},
            stream=False,
            think=False,
        )
        t1 = time.perf_counter()
        warmup_times["DeepSeek-R1"] = t1 - t0
    except Exception as e:
        warmup_times["DeepSeek-R1"] = f"Fehler: {e}"

# ===============================================================
# Gemeinsamer System-Prompt (für OpenAI & DeepSeek identisch)
# ===============================================================
SYSTEM_PROMPT = (
    "Du bist ein sehr strenger Mathe-Korrektor.\n"
    "Aufgabe: Vergleiche 'Antwort des Schülers' mit der 'Korrekte Lösung'.\n"
    "Gib EXAKT nur eines der drei Wörter zurück: korrekt | teilweise korrekt | falsch\n"
    "Kein weiterer Text, keine Begründung, keine Satzzeichen."
)

# ===============================================================
# Ordnerwahl: Klausur-Ordner auswählen
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
# JSON laden (Hilfsfunktion)
# ===============================================================
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
# ===============================================================
# Normalizer: nur Einträge mit "id" durchlassen (Summarys filtern)
# ===============================================================
def _normalize_task_list(raw):
    items = raw if isinstance(raw, list) else ([raw] if isinstance(raw, dict) else [])
    return [it for it in items if isinstance(it, dict) and "id" in it]

# ===============================================================
# OpenAI-Bewertung: vergleicht Antwort mit base_truth
# ===============================================================
def evaluate_with_openai(base, answer, model="gpt-5-mini"):
    prompt = (
        "Vergleiche die beiden:\n"
        f"Korrekte Lösung: {base}\n"
        f"Antwort des Schülers: {answer}\n"
        "Ergebnis wie angewiesen."
    )

    t0 = time.perf_counter()
    respond = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=1.0,  
    )
    t1 = time.perf_counter()

    return respond.choices[0].message.content.strip(), (t1 - t0)

# ===============================================================
# DeepSeek-Bewertung: vergleicht Antwort mit base_truth
# ===============================================================
def evaluate_with_deepseek(base, answer, model=DEEPSEEK_MODEL):
    prompt = (
        "Vergleiche die beiden:\n"
        f"Korrekte Lösung: {base}\n"
        f"Antwort des Schülers: {answer}\n"
        "Ergebnis wie angewiesen."
    )

    try:
        t0 = time.perf_counter()
        response = ollama.chat(
            model=model,
            messages= [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
             options={
                "temperature": 0.1,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
            },
            stream=False,
            think=False,
        )
        t1 = time.perf_counter()

        response = response.message.content.strip(), (t1 - t0)

        return response
    except Exception as e:
        return f"[DeepSeek Fehler] {e}", 0.0

# ===============================================================
# DeepSeek-Bewertung: vergleicht Antwort mit base_truth
# ===============================================================
# def evaluate_with_deepseek_math(base, answer, model=MATH_MODEL):
#     prompt = (
#         "Vergleiche die beiden:\n"
#         f"Korrekte Lösung: {base}\n"
#         f"Antwort des Schülers: {answer}\n"
#         "Ergebnis wie angewiesen."
#     )
#     try:
#         t0 = time.perf_counter()
#         response = ollama.chat(
#             model=model,
#             messages=[
#                 {"role": "system", "content": SYSTEM_PROMPT},
#                 {"role": "user", "content": prompt},
#             ],
#             options={
#                 "temperature": 0.2,
#                 "top_p": 0.9,
#                 "repeat_penalty": 1.1,
#             },
#             stream=False,
#             think=False,
#         )
#         t1 = time.perf_counter()
#         return response.message.content.strip(), (t1 - t0)
#     except Exception as e:
#         return f"[Math Fehler] {e}", 0.0
    
# ===============================================================
# Punktezuweisung auf Basis der Bewertung (robust mit Regex)
# ===============================================================
def assign_points(evaluation_str: str) -> float:
    s = evaluation_str.strip().lower()

    # "teilweise korrekt" zuerst prüfen, weil "korrekt" auch darin vorkommt
    if re.search(r"\bteilweise\b", s) or "partially" in s:
        return 0.5
    elif re.search(r"\bkorrekt\b", s) or "correct" in s:
        return 1.0
    else:
        return 0.0

# ===============================================================
# Hauptaufgaben-ID extrahieren: "aufgabe_12a" -> "aufgabe_12"
# ===============================================================
def get_main_task(task_id: str) -> str:
    m = re.match(r"(aufgabe_\d+)", task_id)
    return m.group(1) if m else task_id

# ===============================================================
# Main: JSON-Antworten verarbeiten
# ===============================================================
def run_for_folder(folder: str):
    klausur_name = folder
    print(f"\n===== Starte Bewertung für Ordner: {folder} =====")

    # JSON-Dateien
    base_json = os.path.join(folder, f"{folder}.json")
    openai_json = os.path.join(folder, f"{folder}_antworten_openai.json")
    deepseek_json = os.path.join(folder, f"{folder}_antworten_deepseek.json")
    math_json    = os.path.join(folder, f"{folder}_antworten_math.json")

    # Nach Ordnerwahl: Pfade & Existenz checken (Prints)
    def _exists(p): return "OK" if os.path.exists(p) else "FEHLT"
    print("Eingelesene/ausgewählte Dateien:")
    print(f"  - Base (Truth):       {base_json} [{_exists(base_json)}]")
    print(f"  - OpenAI Antworten:   {openai_json} [{_exists(openai_json)}]")
    print(f"  - DeepSeek Antworten: {deepseek_json} [{_exists(deepseek_json)}]")
    print(f"  - Math Antworten:     {math_json} [{_exists(math_json)}]")

    # Laden
    base_tasks = load_json(base_json)
    openai_answers = load_json(openai_json)
    deepseek_answers = load_json(deepseek_json)
    math_answers = load_json(math_json)

    # Summary-/Nicht-Aufgaben rausfiltern
    base_tasks       = _normalize_task_list(base_tasks)
    openai_answers   = _normalize_task_list(openai_answers)
    deepseek_answers = _normalize_task_list(deepseek_answers)
    math_answers     = _normalize_task_list(math_answers)

    # id -> antwort Maps
    openai_map        = {a["id"]: a["antwort"] for a in openai_answers}
    deepseek_map      = {a["id"]: a["antwort"] for a in deepseek_answers}
    deepseek_math_map = {a["id"]: a["antwort"] for a in math_answers}
    
    # Container für Ergebnisse der Phasen
    results_openai   = {}  # task_id -> {"openai_on_openai","openai_on_deepseek","openai_on_deepseek_math"}
    results_deepseek = {}  # task_id -> {"deepseek_on_openai","deepseek_on_deepseek"}
    # results_deepseek_math = {}  # AUSKOMMENTIERT: DeepSeek-Math bewertet nicht

    # Zeit-Akkus
    openai_time_total   = 0.0
    deepseek_time_total = 0.0
    # math_time_total     = 0.0  # AUSKOMMENTIERT: kein DeepSeek-Math als Bewerter
    t_openai_for_openai = 0.0
    t_openai_for_deepseek = 0.0
    t_openai_for_deepseek_math = 0.0
    t_deepseek_for_openai = 0.0
    t_deepseek_for_deepseek = 0.0
    
    # ========= PHASE 1: OpenAI bewertet komplette Klausur =========
    print("\n===== PHASE 1: OpenAI bewertet die komplette Klausur =====")
    for task in base_tasks:
        task_id = task["id"]
        base = task.get("base_truth", "")
        openai_ans        = openai_map.get(task_id, "")
        deepseek_ans      = deepseek_map.get(task_id, "")
        deepseek_math_ans = deepseek_math_map.get(task_id, "")

        print(f"[OpenAI] Aufgabe {task_id} …")
        t0 = time.perf_counter()
        eval_openai_on_openai, dt1        = evaluate_with_openai(base, openai_ans)
        eval_openai_on_deepseek, dt2      = evaluate_with_openai(base, deepseek_ans)
        eval_openai_on_deepseek_math, dt3 = evaluate_with_openai(base, deepseek_math_ans)
        # Einzelzeiten addieren
        t_openai_for_openai        += dt1
        t_openai_for_deepseek      += dt2
        t_openai_for_deepseek_math += dt3
        t1 = time.perf_counter()

        results_openai[task_id] = {
            "openai_on_openai":        eval_openai_on_openai,
            "openai_on_deepseek":      eval_openai_on_deepseek,
            "openai_on_deepseek_math": eval_openai_on_deepseek_math,
            "duration_task_openai_phase": t1 - t0
        }
        openai_time_total += (dt1 + dt2 + dt3)
        print(f"  erledigt in {_fmt_duration(t1 - t0)}  (gesamt: {_fmt_duration(openai_time_total)})")

    # ========= PHASE 2: DeepSeek bewertet komplette Klausur =========
    print("\n===== PHASE 2: DeepSeek R1 bewertet die komplette Klausur =====")
    if "DeepSeek-R1" in warmup_times:
        wt = warmup_times["DeepSeek-R1"]
        if isinstance(wt, float):
            print(f"[Warmup] DeepSeek-R1 brauchte {_fmt_duration(wt)} zum Laden")
        else:
            print(f"[Warmup] DeepSeek-R1 fehlgeschlagen: {wt}")

    for task in base_tasks:
        task_id = task["id"]
        base = task.get("base_truth", "")
        openai_ans        = openai_map.get(task_id, "")
        deepseek_ans      = deepseek_map.get(task_id, "")
        # deepseek_math_ans = deepseek_math_map.get(task_id, "")  # AUSKOMMENTIERT: R1 bewertet nicht Math-Antworten

        print(f"[DeepSeek] Aufgabe {task_id} …")
        t0 = time.perf_counter()
        eval_deepseek_on_openai, dt1   = evaluate_with_deepseek(base, openai_ans)
        eval_deepseek_on_deepseek, dt2 = evaluate_with_deepseek(base, deepseek_ans)
        # eval_deepseek_on_deepseek_math, dt3 = evaluate_with_deepseek(base, deepseek_math_ans)  # AUSKOMMENTIERT
        t_deepseek_for_openai   += dt1
        t_deepseek_for_deepseek += dt2
        t1 = time.perf_counter()

        results_deepseek[task_id] = {
            "deepseek_on_openai":   eval_deepseek_on_openai,
            "deepseek_on_deepseek": eval_deepseek_on_deepseek,
            # "deepseek_on_deepseek_math": eval_deepseek_on_deepseek_math,  # AUSKOMMENTIERT
            "duration_task_deepseek_phase": t1 - t0
        }
        deepseek_time_total += (dt1 + dt2)  # + dt3 entfällt
        print(f"  erledigt in {_fmt_duration(t1 - t0)}  (gesamt: {_fmt_duration(deepseek_time_total)})")

    # ========= PHASE 3: DeepSeek-Math bewertet … AUSKOMMENTIERT =========
    # print("\n===== PHASE 3: DeepSeek Math bewertet die komplette Klausur =====")
    # for task in base_tasks:
    #     task_id = task["id"]
    #     base = task.get("base_truth", "")
    #     openai_ans        = openai_map.get(task_id, "")
    #     deepseek_ans      = deepseek_map.get(task_id, "")
    #     deepseek_math_ans = deepseek_math_map.get(task_id, "")
    #
    #     print(f"[DeepSeek-Math] Aufgabe {task_id} …")
    #     t0 = time.perf_counter()
    #     eval_deepseek_math_on_openai, dt1       = evaluate_with_deepseek_math(base, openai_ans)
    #     eval_deepseek_math_on_deepseek, dt2     = evaluate_with_deepseek_math(base, deepseek_ans)
    #     eval_deepseek_math_on_deepseek_math, dt3= evaluate_with_deepseek_math(base, deepseek_math_ans)
    #     t1 = time.perf_counter()
    #
    #     results_deepseek_math[task_id] = {
    #         "deepseek_math_on_openai":        eval_deepseek_math_on_openai,
    #         "deepseek_math_on_deepseek":      eval_deepseek_math_on_deepseek,
    #         "deepseek_math_on_deepseek_math": eval_deepseek_math_on_deepseek_math,
    #         "duration_task_math_phase": t1 - t0
    #     }
    #     math_time_total += (dt1 + dt2 + dt3)
    #     print(f"  erledigt in {_fmt_duration(t1 - t0)}  (gesamt: {_fmt_duration(math_time_total)})")

    # ========= Zusammenführen, Punkte & Summaries =========
    evaluation = []
    group_sums = {}
    total_count = 0
    klausur_sums = {
        "openai_for_openai":         0.0,
        "openai_for_deepseek":       0.0,
        "openai_for_deepseek_math":  0.0,  # OpenAI bewertet auch die Math-Antworten
        "deepseek_for_openai":       0.0,
        "deepseek_for_deepseek":     0.0,
        # "deepseek_for_deepseek_math":    0.0,     # AUSKOMMENTIERT
        # "deepseek_math_for_openai":      0.0,     # AUSKOMMENTIERT
        # "deepseek_math_for_deepseek":    0.0,     # AUSKOMMENTIERT
        # "deepseek_math_for_deepseek_math": 0.0,   # AUSKOMMENTIERT
    }

    for task in base_tasks:
        task_id = task["id"]
        base = task.get("base_truth", "")
        openai_ans        = openai_map.get(task_id, "")
        deepseek_ans      = deepseek_map.get(task_id, "")
        deepseek_math_ans = deepseek_math_map.get(task_id, "")

        # Ergebnisse der Phasen holen
        o = results_openai.get(task_id, {})
        d = results_deepseek.get(task_id, {})
        # m = results_deepseek_math.get(task_id, {})  # AUSKOMMENTIERT

        eval_openai_openai        = o.get("openai_on_openai", "")
        eval_openai_deepseek      = o.get("openai_on_deepseek", "")
        eval_openai_deepseek_math = o.get("openai_on_deepseek_math", "")
        eval_deepseek_openai      = d.get("deepseek_on_openai", "")
        eval_deepseek_deepseek    = d.get("deepseek_on_deepseek", "")
        # eval_deepseek_deepseek_math = d.get("deepseek_on_deepseek_math", "")
        # eval_deepseek_math_openai        = m.get("deepseek_math_on_openai", "")
        # eval_deepseek_math_deepseek      = m.get("deepseek_math_on_deepseek", "")
        # eval_deepseek_math_deepseek_math = m.get("deepseek_math_on_deepseek_math", "") 
        
        # Punkte
        pts_openai_openai        = assign_points(eval_openai_openai)
        pts_openai_deepseek      = assign_points(eval_openai_deepseek)
        pts_openai_deepseek_math = assign_points(eval_openai_deepseek_math)
        pts_deepseek_openai      = assign_points(eval_deepseek_openai)
        pts_deepseek_deepseek    = assign_points(eval_deepseek_deepseek)
        # pts_deepseek_deepseek_math = assign_points(eval_deepseek_deepseek_math)
        # pts_deepseek_math_openai        = assign_points(eval_deepseek_math_openai)
        # pts_deepseek_math_deepseek      = assign_points(eval_deepseek_math_deepseek)
        # pts_deepseek_math_deepseek_math = assign_points(eval_deepseek_math_deepseek_math)
        
        # Evaluationseintrag
        evaluation.append({
            "id": task_id,
            "base_truth": base,
            "openai_answer": openai_ans,
            "deepseek_answer": deepseek_ans,
            "deepseek_math_answer": deepseek_math_ans,  # bleibt, weil OpenAI es bewertet
            "evaluated_by_openai": {
                "openai":        eval_openai_openai,
                "deepseek":      eval_openai_deepseek,
                "deepseek_math": eval_openai_deepseek_math,
                "points": {
                    "openai":        pts_openai_openai,
                    "deepseek":      pts_openai_deepseek,
                    "deepseek_math": pts_openai_deepseek_math
                },
            },
            "evaluated_by_deepseek": {
                "openai":   eval_deepseek_openai,
                "deepseek": eval_deepseek_deepseek,
                # "deepseek_math": eval_deepseek_deepseek_math,  # AUSKOMMENTIERT
                "points": {
                    "openai":   pts_deepseek_openai,
                    "deepseek": pts_deepseek_deepseek,
                    # "deepseek_math": pts_deepseek_deepseek_math  # AUSKOMMENTIERT
                },
            },
            # "evaluated_by_deepseek_math": {
            #    "openai": eval_deepseek_math_openai,
            #    "deepseek": eval_deepseek_math_deepseek,
            #    "deepseek_math": eval_deepseek_math_deepseek_math,
            #    "points": {
            #        "openai": pts_deepseek_math_openai,
            #        "deepseek": pts_deepseek_math_deepseek,
            #        "deepseek_math": pts_deepseek_math_deepseek_math
            #   }
            #}
        })

        # Gruppierung & Summierung
        gid = get_main_task(task_id)
        if gid not in group_sums:
            group_sums[gid] = {"count": 0, "sums": {k:0.0 for k in klausur_sums.keys()}}
        group_sums[gid]["count"] += 1
        group_sums[gid]["sums"]["openai_for_openai"]        += pts_openai_openai
        group_sums[gid]["sums"]["openai_for_deepseek"]      += pts_openai_deepseek
        group_sums[gid]["sums"]["openai_for_deepseek_math"] += pts_openai_deepseek_math
        group_sums[gid]["sums"]["deepseek_for_openai"]      += pts_deepseek_openai
        group_sums[gid]["sums"]["deepseek_for_deepseek"]    += pts_deepseek_deepseek
        # group_sums[gid]["sums"]["deepseek_for_deepseek_math"] += pts_deepseek_deepseek_math  # AUSKOMMENTIERT
        # group_sums[gid]["sums"]["deepseek_math_for_openai"]   += ...
        # group_sums[gid]["sums"]["deepseek_math_for_deepseek"] += ...
        # group_sums[gid]["sums"]["deepseek_math_for_deepseek_math"] += ...

        total_count += 1
        for k, v in group_sums[gid]["sums"].items():
            pass  # strukturell

        klausur_sums["openai_for_openai"]        += pts_openai_openai
        klausur_sums["openai_for_deepseek"]      += pts_openai_deepseek
        klausur_sums["openai_for_deepseek_math"] += pts_openai_deepseek_math

        klausur_sums["deepseek_for_openai"]      += pts_deepseek_openai
        klausur_sums["deepseek_for_deepseek"]    += pts_deepseek_deepseek
        # klausur_sums["deepseek_for_deepseek_math"] += pts_deepseek_deepseek_math

        # klausur_sums["deepseek_math_for_openai"] += pts_deepseek_math_openai
        # klausur_sums["deepseek_math_for_deepseek"] += pts_deepseek_math_deepseek
        # klausur_sums["deepseek_math_for_deepseek_math"] += pts_deepseek_math_deepseek_math
    
    # Genauigkeit je Hauptaufgabe
    group_summary = {}
    print("\n===== Genauigkeit je Hauptaufgabe =====")
    for gid, agg in sorted(group_sums.items(), key=lambda kv: kv[0]):
        n = agg["count"]; max_points = n * 1.0; sums = agg["sums"]
        pct = {k: (v / max_points * 100.0 if max_points > 0 else 0.0) for k, v in sums.items()}
        group_summary[gid] = {
            "teilaufgaben": n,
            "prozent": {k: round(val, 2) for k, val in pct.items()},
            "punkte":  {k: round(v, 3) for k, v in sums.items()},
            "max_punkte": max_points
        }
        print(
            f"- {gid} (n={n}): "
            f"OpenAI→OpenAI {pct['openai_for_openai']:.1f}%, "
            f"OpenAI→DeepSeek {pct['openai_for_deepseek']:.1f}%, "
            f"OpenAI→DeepSeek-Math {pct['openai_for_deepseek_math']:.1f}%; "
            f"DeepSeek→OpenAI {pct['deepseek_for_openai']:.1f}%, "
            f"DeepSeek→DeepSeek {pct['deepseek_for_deepseek']:.1f}%"
            # f"DeepSeek→DeepSeek-Math {pct['deepseek_for_deepseek_math']:.1f}%; "
            # f"DeepSeek-Math→OpenAI {pct['deepseek_math_for_openai']:.1f}%, "
            # f"DeepSeek-Math→DeepSeek {pct['deepseek_math_for_deepseek']:.1f}%, "
            # f"DeepSeek-Math→DeepSeek-Math {pct['deepseek_math_for_deepseek_math']:.1f}%"
        )

    # Gesamtbewertung Klausur
    klausur_max_points = total_count * 1.0
    klausur_pct = {k: (v / klausur_max_points * 100.0 if klausur_max_points > 0 else 0.0)
                   for k, v in klausur_sums.items()}
    klausur_summary = {
        klausur_name: {
            "teilaufgaben": total_count,
            "prozent": {k: round(v, 2) for k, v in klausur_pct.items()},
            "punkte":  {k: round(v, 3) for k, v in klausur_sums.items()},
            "max_punkte": klausur_max_points
        }
    }

    # Warmup sauber extrahieren
    wt = warmup_times.get("DeepSeek-R1", 0.0)
    wt_sec = wt if isinstance(wt, float) else 0.0

    # DeepSeek inkl. Warmup (nur wenn Warmup-Zeit valide ist)
    deepseek_with_warmup_seconds = deepseek_time_total + wt_sec

    # gewünschte Gesamtsummen
    sum_openai_for_openai_and_deepseek   = t_openai_for_openai + t_openai_for_deepseek
    sum_deepseek_for_openai_and_deepseek = t_deepseek_for_openai + t_deepseek_for_deepseek
    sum_openai_for_deepseek_math         = t_openai_for_deepseek_math

    # Gesamtdauer
    print("\n===== Gesamtdauer der Bewertungen =====")
    print(f"OpenAI-Bewertung: {_fmt_duration(openai_time_total)}")
    print(f"DeepSeek-Bewertung: {_fmt_duration(deepseek_time_total)}")
    # print(f"DeepSeek-Math-Bewertung: {_fmt_duration(math_time_total)}")  # AUSKOMMENTIERT
    print("\nAggregierte Kontroll-Zeiten (Summen):")
    print(f"OpenAI für OpenAI & DeepSeek: {_fmt_duration(sum_openai_for_openai_and_deepseek)}")
    print(f"DeepSeek für OpenAI & DeepSeek: {_fmt_duration(sum_deepseek_for_openai_and_deepseek)}")
    print(f"OpenAI für DeepSeek-Math: {_fmt_duration(sum_openai_for_deepseek_math)}")
    if wt_sec > 0:
        print(f"\nWarmup DeepSeek-R1: {_fmt_duration(wt_sec)}")
        print(f"DeepSeek inkl. Warmup: {_fmt_duration(deepseek_with_warmup_seconds)}")
    
    # Summary anhängen & speichern
    evaluation.append({"group_summary": group_summary})
    evaluation.append({"klausur_summary": klausur_summary})
    evaluation.append({
        "timing_summary": {
            "openai_seconds":               round(openai_time_total, 3),
            "deepseek_seconds":             round(deepseek_time_total, 3),
            "warmup_deepseek_r1_seconds":   round(wt_sec, 3),
            "deepseek_with_warmup_seconds": round(deepseek_with_warmup_seconds, 3),

            # "math_seconds":     round(math_time_total, 3),  # AUSKOMMENTIERT
            "sum_openai_for_openai_and_deepseek_seconds":   round(sum_openai_for_openai_and_deepseek, 3),
            "sum_deepseek_for_openai_and_deepseek_seconds": round(sum_deepseek_for_openai_and_deepseek, 3),
            "sum_openai_for_deepseek_math_seconds":         round(sum_openai_for_deepseek_math, 3),

            "openai_human":                _fmt_duration(openai_time_total),
            "deepseek_human":              _fmt_duration(deepseek_time_total),
            "warmup_deepseek_r1_human":    _fmt_duration(wt_sec),
            "deepseek_with_warmup_human":  _fmt_duration(deepseek_with_warmup_seconds),

            # "math_human":     _fmt_duration(math_time_total),  # AUSKOMMENTIERT
            "sum_openai_for_openai_and_deepseek_human":   _fmt_duration(sum_openai_for_openai_and_deepseek),
            "sum_deepseek_for_openai_and_deepseek_human": _fmt_duration(sum_deepseek_for_openai_and_deepseek),
            "sum_openai_for_deepseek_math_human":         _fmt_duration(sum_openai_for_deepseek_math),

            # Warmup separat & kombiniert


           

        }
    })

    out_file = os.path.join(folder, f"{folder}_bewertung_ai.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(evaluation, f, indent=2, ensure_ascii=False)
    print(f"\nBewertung gespeichert in {out_file}")

# ===============================================================
# Main: genau EIN Ordner + Warmup im Hintergrund
# ===============================================================
if __name__ == "__main__":
    # Warmup nur für R1 im Hintergrund starten
    threading.Thread(target=warmup_deepseek_r1, daemon=True).start()

    # Genau EINEN Ordner wählen
    folder = choose_klausur_folder()

    t_global_start = time.perf_counter()
    run_for_folder(folder)
    t_global_end = time.perf_counter()
    print(f"\nGesamtlaufzeit: {_fmt_duration(t_global_end - t_global_start)}")
