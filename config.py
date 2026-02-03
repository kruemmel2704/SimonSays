# config.py
from gpiozero import LED, Button

# Definition der GPIO Pins (BCM Nummerierung)
# Format: Farbe: (LED_PIN, BUTTON_PIN)
HARDWARE_SETUP = {
    "red": {"led": 17, "btn": 18},
    "green": {"led": 27, "btn": 22},
    "blue": {"led": 23, "btn": 24},
    "yellow": {"led": 25, "btn": 5}
}

# Geschwindigkeitseinstellungen (in Sekunden)
FLASH_DELAY = 0.5
SEQUENCE_PAUSE = 0.3