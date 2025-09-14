# Installation

## 1. Virtuelle Umgebung anlegen
```bash
python -m venv .venv
```

### Aktivieren:
- **Windows PowerShell**
  ```powershell
  .venv\Scripts\activate
  ```
- **macOS/Linux (bash/zsh)**
  ```bash
  source .venv/bin/activate
  ```

---

## 2. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

👉 Tipp: Falls Probleme auftreten, `pip` erst updaten:
```bash
python -m pip install --upgrade pip
```

---

## 3. (Optional) Nur bestimmte Extras installieren
Falls du nur Teile der Funktionen benötigst, kannst du gezielt einzelne Pakete installieren:

- **Tabellen/Excel**  
  ```bash
  pip install pandas numpy openpyxl
  ```

- **PDF/Parsing**  
  ```bash
  pip install pypdf pdfminer.six regex
  ```

- **Lokale Modelle (DeepSeek via Ollama)**  
  ```bash
  pip install ollama
  ```

- **Plots**  
  ```bash
  pip install matplotlib
  ```

---

✅ Damit bist du startklar und kannst die Skripte mit den benötigten Bibliotheken ausführen.
