# Wir nutzen Python 3.11 auf Bookworm für beste Kompatibilität mit Kernel 6.12
FROM python:3.11-slim-bookworm

# Arbeitsverzeichnis im Container
WORKDIR /app

# System-Abhängigkeiten installieren
# - gcc & python3-dev: Zum Kompilieren von GPIO und Socket-Erweiterungen
# - libgpiod-dev & python3-libgpiod: Für den modernen Hardware-Zugriff
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libgpiod-dev \
    python3-libgpiod \
    && rm -rf /var/lib/apt/lists/*

# Python-Bibliotheken installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere die gesamte Ordnerstruktur in den Container
# (Dadurch werden /app, run.py, etc. übernommen)
COPY . .

# Port 5000 für Flask/Socket.IO nach außen öffnen
EXPOSE 5000

# Startbefehl: Wir rufen die run.py im Wurzelverzeichnis auf
CMD ["python", "run.py"]