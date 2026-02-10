# app/config.py
from gpiozero import LED, Button, Buzzer
 
# Definition der GPIO Pins (BCM Nummerierung)
# Diese Struktur erlaubt es der gpio_logic, dynamisch über Farben zu iterieren.
HARDWARE_SETUP = {
    "red": {
        "led": 17, 
        "btn": 18
    },
    "green": {
        "led": 27, 
        "btn": 22
    },
    "blue": {
        "led": 23, 
        "btn": 24
    },
    "yellow": {
        "led": 25, 
        "btn": 5
    }
}

# Pin für den aktiven Buzzer
BUZZER_PIN = 6

# Standard-Timings (Startwerte für "Medium")
FLASH_DELAY = 0.5
SEQUENCE_PAUSE = 0.3

# Schwierigkeitsstufen für die Flask-Erweiterung
DIFFICULTY_SETTINGS = {
    "easy": {
        "flash": 0.8,
        "pause": 0.5
    },
    "medium": {
        "flash": 0.5,
        "pause": 0.3
    },
    "hard": {
        "flash": 0.2,
        "pause": 0.1
    }
}

# Pfad zur Highscore-Datei (wird im Docker-Container in /app/ gespeichert)
HIGHSCORE_FILE = "highscores.json"