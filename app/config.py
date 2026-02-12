# app/config.py
import platform
import os
from gpiozero import LED, Button, Buzzer

IS_RASPI = platform.machine().startswith('arm') or platform.machine().startswith('aarch64')

# Falls du auf Windows/Mac testest, erzwinge IS_RASPI = False
if os.name == 'nt': 
    IS_RASPI = False

# MySQL Datenbank Konfiguration
DB_CONFIG = {
    'host': 'plesk01.sn-datacom.de',
    'database': 'bbs_simonsays',
    'user': 'bbs_simonsays_user',
    'password': 'Bv6pSqVkyhx13?&z',
    'port': 3306
}

# Definition der GPIO Pins (BCM Nummerierung)
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