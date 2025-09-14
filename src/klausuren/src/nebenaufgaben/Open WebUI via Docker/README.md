# Open WebUI per Docker – Setup & Nutzung

Diese Anleitung zeigt, wie du **Open WebUI** als Docker-Container startest und mit **Ollama** verbindest. Du hast zwei Wege:
1. **Trenne** Open WebUI und Ollama (empfohlen, wenn Ollama schon läuft)
2. **Bundle** beides in einem Container (einfachster Einstieg)

---

## Voraussetzungen
- **Docker** & (optional) **Docker Compose**
- Für GPU: aktuelle **NVIDIA-Treiber** + **nvidia-container-toolkit**

---

## Option A: Open WebUI + externes Ollama (empfohlen)

### 1) Docker Run (CPU)
    docker run -d \
      -p 3000:8080 \
      -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
      -v open-webui:/app/backend/data \
      --name open-webui \
      --restart always \
      ghcr.io/open-webui/open-webui:main

### 2) Docker Run (GPU, CUDA)
    docker run -d \
      -p 3000:8080 \
      --gpus all \
      --add-host=host.docker.internal:host-gateway \
      -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
      -v open-webui:/app/backend/data \
      --name open-webui \
      --restart always \
      ghcr.io/open-webui/open-webui:cuda

> **Hinweis:** `OLLAMA_BASE_URL` zeigt auf deinen lokalen Ollama-Dienst (Standard: `http://localhost:11434`).  
> Im Container entspricht das `host.docker.internal`.

### 3) Open WebUI öffnen
- Browser: **http://localhost:3000**
- Im UI: **Admin Settings → Connections → Ollama** → Verbindung prüfen / Modelle verwalten

---

## Option B: Open WebUI **inkl. Ollama** (ein Container)
Praktisch für schnelle Tests, da Ollama direkt im Container mitläuft:

```bash
docker run -d   -p 3000:8080   -v ollama:/root/.ollama   -v open-webui:/app/backend/data   --name open-webui   --restart always   ghcr.io/open-webui/open-webui:ollama
```

---

## Option C: Manuelles Build & Start (falls du Änderungen am Image hast)
```bash
# 1) Docker-Image bauen
docker build -t open-webui-fixed .

# 2) Container starten (GPU-Beispiel)
docker run -d   -p 3000:8080   --gpus all   -v open-webui:/app/backend/data   --name webui-fixed   open-webui-fixed

# 3) Logs anzeigen
docker logs -f webui-fixed
```

> Für CPU den Parameter `--gpus all` einfach weglassen.

---

## Docker Compose Beispiele

Speichere eine `docker-compose.yml` und starte mit:
```bash
docker compose up -d
```
Stoppen & Entfernen:
```bash
docker compose down
```

### Variante 1 (einfach & universell)
```yaml
services:
  openwebui:
    # Image wählen:
    # - CPU: ghcr.io/open-webui/open-webui:main
    # - GPU: ghcr.io/open-webui/open-webui:cuda
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    restart: always
    ports:
      - "3000:8080"
    environment:
      OLLAMA_BASE_URL: "http://host.docker.internal:11434"
    volumes:
      - openwebui_data:/app/backend/data
    extra_hosts:
      - "host.docker.internal:host-gateway"

volumes:
  openwebui_data:
```

> **Hinweis (GPU mit Variante 1):** Wenn du `:cuda` nutzt, muss dein Docker/Compose GPU-Zugriff unterstützen.  
> Bei `docker run` würdest du zusätzlich `--gpus all` angeben – bei Compose passiert das **nicht automatisch**.  
> Falls GPU nicht erkannt wird, nutze Variante 2.

### Variante 2 (GPU mit Ressourcen-Reservation, Compose v3+ / Swarm)
```yaml
services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:cuda
    container_name: open-webui
    restart: always
    ports:
      - "3000:8080"
    environment:
      OLLAMA_BASE_URL: "http://host.docker.internal:11434"
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: ["gpu"]
    runtime: nvidia
    volumes:
      - openwebui_data:/app/backend/data
    extra_hosts:
      - "host.docker.internal:host-gateway"

volumes:
  openwebui_data:
```

> **Hinweis:** Diese Variante ist die „korrektere“ GPU-Nutzung, funktioniert aber nur mit **Docker Swarm** oder **Compose-Versionen**, die `deploy.resources` unterstützen.

---

## Erste Schritte in Open WebUI
1. **http://localhost:3000** öffnen → Account anlegen / anmelden
2. **Admin Settings → Connections → Ollama**
   - „Manage“ → **Modelle laden** (`ollama pull …`), auswählen, testen
3. **Chat starten** → Modell wählen → prompten

---

## Update
Manuell aktualisieren:
```bash
docker pull ghcr.io/open-webui/open-webui:main
docker stop open-webui && docker rm open-webui
# Danach den ursprünglichen docker run Befehl erneut ausführen
```
Oder **Watchtower** nutzen (automatische Updates).

---

## Troubleshooting
- **Keine Verbindung zu Ollama?**
  - Prüfen: `curl http://localhost:11434/api/tags` am Host
  - In Container-Variante A: `OLLAMA_BASE_URL=http://host.docker.internal:11434` setzen
  - Firewall/Proxy prüfen
- **Port 3000 belegt?**
  - Mapping anpassen, z. B. `-p 3001:8080`
- **GPU wird nicht erkannt?**
  - `--gpus all` + NVIDIA Toolkit prüfen
  - Bei Compose ggf. Variante 2 nutzen
- **Im UI kein Modell gelistet?**
  - Unter *Connections → Ollama → Manage* ein Modell **pullen** und aktiv setzen

---

## Links
- Offizielle Quick Start: https://docs.openwebui.com/getting-started/quick-start/
- Starting with Ollama: https://docs.openwebui.com/getting-started/quick-start/starting-with-ollama/
- GitHub (Run-Beispiele): https://github.com/open-webui/open-webui
- Updates: https://docs.openwebui.com/getting-started/updating/
