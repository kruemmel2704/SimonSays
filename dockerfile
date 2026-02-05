# Wir nutzen Bookworm (Debian 12), das ist stabiler für moderne Kernel
FROM python:3.11-slim-bookworm

WORKDIR /app

# Installation der System-Abhängigkeiten
# libgpiod-dev und gcc sind notwendig, um die GPIO-Bibliotheken zu bauen
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libgpiod-dev \
    python3-libgpiod \
    && rm -rf /var/lib/apt/lists/*

# Python Abhängigkeiten installieren
COPY requirements.txt .
# --break-system-packages ist bei Bookworm manchmal nötig, im venv aber sauberer. 
# Hier im Container ist es okay, es direkt zu installieren.
RUN pip install --no-cache-dir -r requirements.txt

# Skripte kopieren
COPY Config.py .
COPY SimonSay.py .

# Startbefehl
CMD ["python", "SimonSay.py"]