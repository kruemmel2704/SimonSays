# Wir nutzen ein schlankes Python Image (kompatibel mit ARM/Raspi)
FROM python:3.9-slim

# Arbeitsverzeichnis im Container setzen
WORKDIR /app

# Systemabhängigkeiten installieren (wichtig für GPIO Zugriff)
RUN apt-get update && apt-get install -y \
    gcc \
    libgpiod2 \
    && rm -rf /var/lib/apt/lists/*

# Python Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere deine Skripte in den Container
COPY Config.py .
COPY SimonSay.py .

# Startbefehl
CMD ["python", "SimonSay.py"]