# app/config.py
import platform
import os

# Setze Pin Factory auf Mock, BEVOR gpiozero importiert wird oder Hardware initialisiert wird
IS_RASPI = platform.machine().startswith('arm') or platform.machine().startswith('aarch64')
if os.name == 'nt': 
    IS_RASPI = False

if not IS_RASPI:
    # Dies verhindert, dass gpiozero nach RPi.GPIO sucht und abstürzt
    os.environ['GPIOZERO_PIN_FACTORY'] = 'mock'
    # os.environ['GPIOZERO_PIN_FACTORY'] = 'native' # Alternative falls mock zickt

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


# Datenbank-Konfiguration
import os
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'simon.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False