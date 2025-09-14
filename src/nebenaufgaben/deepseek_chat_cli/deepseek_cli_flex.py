import requests
import threading
import sys

# ===============================================================
# Modelle (eine Zeile aktiv lassen, die andere auskommentieren)
# ===============================================================
DEEPSEEK_MODEL = "deepseek-r1:32b"
MATH_MODEL     = "t1c/deepseek-math-7b-rl:latest"

MODEL = DEEPSEEK_MODEL
# MODEL = MATH_MODEL

# ===============================================================
# Endpoints (eine Variante aktiv lassen)
# ===============================================================
# OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_URL = "http://localhost:11434/api/chat"

# ===============================================================
# Gemeinsame Options
# ===============================================================
OPTIONS = {
    "temperature": 0.1,
    "top_p": 0.9,
    "repeat_penalty": 1.1,
    "num_predict": 320,
    # "format": "json",
    "stop": ["```"]
}
THINK = False
TIMEOUT_S = 120

# ===============================================================
# System Promt (für /chat)
# ===============================================================
SYSTEM_PROMPT_DE = "Antworte ausschließlich auf Deutsch. Sei präzise und knapp."

# ... in main() direkt nach history = []
history = [{"role": "system", "content": SYSTEM_PROMPT_DE}]

# ===============================================================
# Spinner (während DeepSeek läuft)
# ===============================================================
def _spinner_worker(stop_event: threading.Event, label: str = "DeepSeek arbeitet…"):
    frames = "|/-\\"
    i = 0
    while not stop_event.is_set():
        sys.stdout.write("\r" + f"{label} {frames[i % len(frames)]}")
        sys.stdout.flush()
        i += 1
        stop_event.wait(0.2)
    # Zeile leeren, wenn fertig
    sys.stdout.write("\r" + " " * (len(label) + 4) + "\r")
    sys.stdout.flush()

# ===============================================================
# Request-Funktionen
# ===============================================================
def call_generate(prompt: str) -> requests.Response:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "options": OPTIONS,
        "stream": False,
        "think": THINK
    }
    return requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_S)

def call_chat(prompt: str, history=None) -> requests.Response:
    if history is None:
        history = []
    messages = history + [{"role": "user", "content": prompt}]
    payload = {
        "model": MODEL,
        "messages": messages,
        "options": OPTIONS,
        "stream": False,
        "think": THINK
    }
    return requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_S)

def parse_response(resp: requests.Response) -> str:
    resp.raise_for_status()
    data = resp.json()
    if "response" in data:  # /generate
        return (data.get("response") or "").strip()
    msg = data.get("message") or {}
    return (msg.get("content") or "").strip()

# ===============================================================
# CLI-Loop
# ===============================================================
def main():
    print("DeepSeek CLI (Ollama)")
    print(f"Modus: {'/api/chat' if OLLAMA_URL.endswith('/chat') else '/api/generate'}")
    print(f"Modell: {MODEL}")
    print("Mit 'exit', 'quit', 'ende' oder 'bye' beenden.\n")

    history = []

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBeende Chat...")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "ende", "bye"}:
            print("Beende Chat...")
            break

        # Spinner starten
        stop_event = threading.Event()
        spinner = threading.Thread(target=_spinner_worker, args=(stop_event,))
        spinner.start()

        try:
            if OLLAMA_URL.endswith("/chat"):
                resp = call_chat(user_input, history=history)
                text = parse_response(resp)
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": text})
            else:
                resp = call_generate(user_input)
                text = parse_response(resp)
        except Exception as e:
            text = f"[Fehler] {e}"

        # Spinner stoppen
        stop_event.set()
        spinner.join()

        print("\nAntwort:\n" + text + "\n")

# ===============================================================
# Wrapper-Funktion für Jupyter Notebook (mit History)
# ===============================================================
def get_model_response(prompt: str, history=None):
    if history is None:
        history = []
    if not history or history[0].get("role") != "system":
        history.insert(0, {"role": "system", "content": SYSTEM_PROMPT_DE})

    if OLLAMA_URL.endswith("/chat"):
        # Anfrage mit History
        resp = call_chat(prompt, history=history)
        text = parse_response(resp)
        # History erweitern
        history.append({"role": "user", "content": prompt})
        history.append({"role": "assistant", "content": text})
    else:
        resp = call_generate(prompt)
        text = parse_response(resp)
        # bei /generate keine echte History → nur anhängen, wenn du magst
        history.append({"role": "user", "content": prompt})
        history.append({"role": "assistant", "content": text})

    return text, history


if __name__ == "__main__":
    main()
