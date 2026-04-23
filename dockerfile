FROM python:3.11-slim-bookworm

WORKDIR /workspace

RUN apt-get update && apt-get install -y \
    gcc python3-dev libgpiod-dev python3-libgpiod \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiert den kompletten Inhalt (inkl. app-Ordner und run.py)
COPY . .

ENV PYTHONPATH=/workspace
EXPOSE 5000

CMD ["python", "run.py"]