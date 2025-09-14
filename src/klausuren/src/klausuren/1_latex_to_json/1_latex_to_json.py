import os
import re
import openai
import time
import json
import sys        
import threading 

# ==========================================
# Zeitformatierung
# ==========================================
def _fmt_duration(seconds: float) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(int(m), 60)
    ms = int((seconds - int(seconds)) * 1000)
    if h:
        return f"{h}h {m}m {int(s)}s"
    if m:
        return f"{m}m {int(s)}s"
    return f"{int(s)}s {ms}ms"

# ==========================================
# Spinner (während OpenAI läuft)
# ==========================================
def _spinner_worker(stop_event: threading.Event, label: str = "OpenAI arbeitet…"):
    frames = "|/-\\"
    i = 0
    while not stop_event.is_set():
        sys.stdout.write("\r" + f"{label} {frames[i % len(frames)]}")
        sys.stdout.flush()
        i += 1
        # alle 200ms ein neuer Frame
        stop_event.wait(0.2)
    # Zeile „aufräumen“
    sys.stdout.write("\rOpenAI fertig!          \n")
    sys.stdout.flush()

# ==========================================
# Semester-Ordner mit Lated Datei finden
# ==========================================
def find_semester_dirs(base_path="."):
    # Suche alle Ordner mit Prefix SS_ oder WS_
    return [d for d in os.listdir(base_path) if os.path.isdir(d) and (d.startswith("SS_") or d.startswith("WS_"))]

def select_directory(directories):
    print("Verfügbare Semesterordner:")
    for i, d in enumerate(directories):
        print(f"{i+1}: {d}")
    choice = int(input("Bitte Nummer eines Ordners eingeben: ")) - 1
    return directories[choice]

def get_semester_code(selected):
    # Extrahiere "ss_23" oder "ws_23" aus selected, auch wenn selected z.B. "WS23" oder "WS24" ist
    match = re.match(r"(ss|ws)(_?)(\d{2})", selected.lower())
    if match:
        return f"{match.group(1)}{match.group(2)}{match.group(3)}"
    else:
        return selected.lower()

# ==========================================
# Haupt-LaTeX Datei analysieren
# ==========================================    
def extract_input_order_mapping(main_tex_path):
    # Extrahiere die Reihenfolge der eingebundenen Dateien aus einer Haupt-LaTeX-Datei
    mapping = {}
    try:
        with open(main_tex_path, "r", encoding="utf-8") as f:
            content = f.read()
        input_files = re.findall(r"\\input\{(.*?)\}", content)
        for idx, path in enumerate(input_files, 1):
            basename = os.path.basename(path)
            filename_noext = os.path.splitext(basename)[0]
            mapping[filename_noext] = idx
    except FileNotFoundError:
        print(f"Hauptdatei {main_tex_path} nicht gefunden!")
    return mapping

# ==========================================
# LaTeX Dateien lesen und auflisten
# ==========================================
def read_full_file(filepath):
    # Liest den kompletten Inhalt einer .tex Datei ein
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def process_latex_folder(folder_path, file_to_number_map):
    aufgaben_liste = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".tex"):
            full_path = os.path.join(folder_path, filename)
            file_id = os.path.splitext(filename)[0]
            aufgabe_index = file_to_number_map.get(file_id)

            if not aufgabe_index:
                print(f"Keine Nummerierung für Datei {file_id}, wird übersprungen.")
                continue

            print(f"→ Verarbeite Datei: {filename} (Index {aufgabe_index})")
            content = read_full_file(full_path)
            aufgaben_liste.append((aufgabe_index, filename, content))

    return aufgaben_liste

# ==========================================
# ChatGPT Prompt vorbereiten
# ==========================================
def build_prompt():
    return (
        "Du erhältst den gesamten Inhalt einer Mathe-Klausur in LaTeX.\n\n"
        "Deine Aufgabe ist es, die Daten in ein JSON-Format zu extrahieren.\n\n"
        "Regeln:\n"
        "1. Jede Aufgabe wird durch \\begin{Aufgabe} ... \\end{Aufgabe} definiert.\n"
        "2. Wenn eine Aufgabe einleitende Informationen enthält (z. B. ein Anfangswertproblem, Hinweise, Formeln), "
        "dann gelten diese Informationen für **alle Teilaufgaben** dieser Aufgabe.\n"
        "   - Beispiel: Wenn eine Aufgabe mit 'Gegeben ist das Anfangswertproblem ...' beginnt und danach mehrere "
        "   Teilaufgaben (a, b, c) folgen, dann füge diesen Einleitungstext bei jeder Teilaufgabe in das Feld 'frage' ein.\n"
        "3. Jede Teilaufgabe wird durch \\item im enumerate-Block innerhalb von \\begin{Aufgabe} definiert.\n"
        "4. Jede Lösung wird durch \\Loesung{}{} mit eigenem enumerate-Block angegeben. "
        "5. **Wichtig:** Alle mathematischen Ausdrücke sollen in vollständig lesbare Form gebracht werden:\n"
        "   - Brüche \\frac{a}{b} → (a / b)\n"
        "   - Malzeichen \\cdot → *\n"
        "   - Potenzen x^{2} → x^2\n"
        "   - e^{...} → exp(...)\n"
        "   - pi bleibt pi\n"
        "   - komplexe Zahlen i bleiben i\n"
        "   - c_k = ((-1)^k - 1) / (2 * k * pi) * i (kein LaTeX)\n"
        "6. Das JSON-Format soll wie folgt aussehen:\n\n"
        "[\n"
        "  {\n"
        "    'id': 'aufgabe_2a',\n"
        "    'frage': 'Gesamter Text der Aufgabe + relevanter Einleitungstext für Teilaufgabe a',\n"
        "    'lösungsschritte': 'Alle Schritte der Lösung für Teilaufgabe a',\n"
        "    'base_truth': 'Endergebnis der Lösung für Teilaufgabe a'\n"
        "  },\n"
        "  {\n"
        "    'id': 'aufgabe_2b',\n"
        "    'frage': 'Gesamter Text der Aufgabe + relevanter Einleitungstext für Teilaufgabe b',\n"
        "    'lösungsschritte': 'Alle Schritte der Lösung für Teilaufgabe b',\n"
        "    'base_truth': 'Endergebnis der Lösung für Teilaufgabe b'\n"
        "  }\n"
        "]\n\n"
        "müssen lesbar sein."
    )


# ==========================================
# ChatGPT Integration OpenAI API ansprechen
# ==========================================
def send_to_openai(tex_content, prompt, output_json_filename):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Bitte setze die Umgebungsvariable OPENAI_API_KEY")  
    client = openai.OpenAI(api_key=api_key)

    # Spinner starten
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=_spinner_worker, args=(stop_event,), daemon=True)
    spinner_thread.start()

    t0 = time.perf_counter()  # <-- Timer Start

    try:
        # Anfrage an OpenAI
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "Du bist ein hilfreicher Assistent, der LaTeX-Matheaufgaben in JSON umwandelt."},
                {"role": "user", "content": f"{prompt}\n\nHier ist die Klausur:\n{tex_content}"}
            ],
            temperature=1
        )

    finally:
        # Spinner immer stoppen, auch bei Exception
        t1 = time.perf_counter() # <-- Timer Ende
        stop_event.set()
        spinner_thread.join()

    result = response.choices[0].message.content

    with open(output_json_filename, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"\nChatGPT-JSON gespeichert in:\n{output_json_filename}")
    print(f"OpenAI-Aufruf dauerte: {_fmt_duration(t1 - t0)}") 

    # Dauer in Sekunden zurückgeben
    return result, t1 - t0

# ==========================================
# Hauptprogramm
# ==========================================
def main():
    semester_dirs = find_semester_dirs()
    if not semester_dirs:
        print("Keine Semesterordner gefunden (SS_*/WS_*)")
        return

    selected = select_directory(semester_dirs)
    base_path = os.path.join(selected, selected)

    t_global_start = time.perf_counter()  # <-- Start Gesamt

    semester_code = get_semester_code(selected)
    hauptdatei_path = os.path.join(base_path, "M2_SWB_TIB", f"m2_swb_tib_{semester_code}.tex")
    print(f"\nHauptdatei: {semester_code}")
    file_to_number_map = extract_input_order_mapping(hauptdatei_path)

    folders_to_process = ["M2_IT", "M2_SWB_TIB"]
    all_tasks = []

    for folder in folders_to_process:
        full_path = os.path.join(base_path, folder)
        if os.path.exists(full_path):
            print(f"\nScanne Ordner: {folder}")
            aufgaben = process_latex_folder(full_path, file_to_number_map)
            all_tasks.extend(aufgaben)
        else:
            print(f"Ordner nicht gefunden: {full_path}")

    if all_tasks:
        # Sortiere nach Index
        all_tasks.sort(key=lambda x: x[0])

        # Ordner für diese Klausur anlegen
        klausur_folder = f"mathe_2_klausur_{selected}"
        os.makedirs(klausur_folder, exist_ok=True)

        merged_filename = os.path.join(klausur_folder, f"{klausur_folder}.tex")
        with open(merged_filename, "w", encoding="utf-8") as f:
            f.write(f"Mathe 2 Klausur {semester_code}\n\n")
            for idx, (nummer, filename, content) in enumerate(all_tasks, start=1):
                f.write(f"{idx}. Aufgabe ({filename})\n")
                f.write(content)
                f.write("\n\n")
        print(f"\n{len(all_tasks)} Dateien zusammengeführt in:\n{merged_filename}")

        # Jetzt mit OpenAI verarbeiten
        prompt = build_prompt()
        json_output = os.path.join(klausur_folder, f"{klausur_folder}.json")
        tex_content = read_full_file(merged_filename)

        # <-- OpenAI aufrufen und Dauer bekommen
        result_text, openai_secs = send_to_openai(tex_content, prompt, json_output)

        # Gesamtzeit stoppen
        t_global_end = time.perf_counter()
        total_secs = t_global_end - t_global_start

        # Summary-Block bauen (wie in Skript 3)
        summary = {
            "summary": {
                "openai_seconds": round(openai_secs, 3),
                "openai_human": _fmt_duration(openai_secs),
                "total_seconds": round(total_secs, 3),
                "total_human": _fmt_duration(total_secs),
            }
        }

        # Ergebnis parsen und summary anhängen
        try:
            data = json.loads(result_text)
        except Exception:
            data = result_text  # falls kein valides JSON (sollte selten sein)

        if isinstance(data, list):
            data.append(summary)
        else:
            data = [data, summary]

        # Datei mit angehängtem Summary überschreiben
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    else:
        print("Keine Dateien gefunden.")
        # auch hier Gesamtzeit ausgeben
        t_global_end = time.perf_counter()
        print(f"\nGesamtlaufzeit: {_fmt_duration(t_global_end - t_global_start)}")

if __name__ == "__main__":
    main()