# app/config.py
import platform
import os

# Setze Pin Factory auf Mock, BEVOR gpiozero importiert wird oder Hardware initialisiert wird
# Apple Silicon Macs also report 'arm64', so we check for 'Linux' as well
machine = platform.machine().lower()
system = platform.system().lower()

IS_RASPI = False
if system == "linux":
    # Check for Raspberry Pi specifically, not just ARM architecture
    if os.path.exists('/proc/device-tree/model'):
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read().lower()
                if "raspberry pi" in model:
                    IS_RASPI = True
        except:
            pass

# Fallback check for architecture if /proc is not accessible
if not IS_RASPI and ("arm" in machine or "aarch64" in machine) and system == "linux":
    # If it's ARM Linux but NOT confirmed Pi, we default to False unless overridden
    IS_RASPI = os.environ.get('FORCE_RASPI', '0') == '1'

if system == 'darwin' or os.name == 'nt': 
    IS_RASPI = False

if not IS_RASPI:
    # Dies verhindert, dass gpiozero nach RPi.GPIO sucht und abstürzt
    os.environ['GPIOZERO_PIN_FACTORY'] = 'mock'

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


# Physische Knöpfe für Schwierigkeitsgrad
DIFFICULTY_BUTTONS = {
    "easy": 12,
    "medium": 13,
    "hard": 16
}

# SNES Controller Konfiguration
SNES_PINS = {
    "LATCH": 9,
    "CLOCK": 11,
    "DATA": 10
}

# Mapping: Welcher SNES-Button macht was im Spiel?
SNES_MAPPING = {
    "Y": "green",
    "A": "red",
    "X": "blue",
    "B": "yellow",
    "START": "START_SIGNAL"
}

# Datenbank-Konfiguration
import os
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'simon.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False