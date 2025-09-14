# Setup: Ollama + DeepSeek

## 1) Ollama installieren und starten
- Download & Anleitung: https://ollama.com
- Standard-Host: `http://localhost:11434` (kann per `OLLAMA_HOST` geändert werden)

**macOS (brew):**
```bash
brew install ollama
ollama serve   # startet den Dienst im Vordergrund
```

**Linux (curl installer):**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
```

**Windows:**
- Installer von der Website laden und ausführen.
- Danach „Ollama“ App starten (bzw. als Dienst einrichten).

**Health-Check (optional):**
```bash
curl http://localhost:11434/api/tags
```

---

## 2) Modelle laden
```bash
ollama pull deepseek-r1:32b
ollama pull t1c/deepseek-math-7b-rl:latest
```

> Tipp: Der erste Pull kann einige GB laden – Geduld und genügend Speicher einplanen.

---

## 3) Funktionstest
```bash
ollama run deepseek-r1:32b "Sag Hallo"
ollama run t1c/deepseek-math-7b-rl:latest "2+2?"
```

---

## 4) Häufige Probleme
- **Port belegt**: Stelle sicher, dass nichts anderes auf `11434` läuft oder setze `OLLAMA_HOST=http://127.0.0.1:PORT`.
- **VRAM zu klein**: Nutze eine kleinere Variante (falls verfügbar) oder greife per API auf ein gehostetes Modell zurück.
- **Langsamer Erststart**: Der erste Run initialisiert Gewichte im Speicher – Folgeläufe sind schneller.
