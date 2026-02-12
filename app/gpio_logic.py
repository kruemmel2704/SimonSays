import time
import random
import threading
import platform
from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory

# Wir importieren die Konfiguration
from app.config import HARDWARE_SETUP, BUZZER_PIN, FLASH_DELAY, SEQUENCE_PAUSE

# --- AUTOMATISCHE HARDWARE-ERKENNUNG & EMULATION ---
try:
    from gpiozero import LED, Button, Buzzer
    # Teste ob wir wirklich Hardware-Zugriff haben
    test_buzzer = Buzzer(BUZZER_PIN)
    Device.pin_factory = LGPIOFactory()
    IS_HARDWARE = True
    print("SIMON SAYS: Echte Hardware erkannt.")
except (ImportError, Exception):
    IS_HARDWARE = False
    print("SIMON SAYS: Keine Hardware gefunden. Emulations-Modus aktiv.")
    

    # Dummy-Klassen für den PC-Modus
    class LED:
        def __init__(self, pin): self.pin = pin
        def on(self): pass
        def off(self): pass

    class Buzzer:
        def __init__(self, pin): self.pin = pin
        def on(self): pass
        def off(self): pass

    class Button:
        def __init__(self, pin): self.pin = pin
        @property
        def is_pressed(self): return False # Web-Input wird separat gehandelt

# ---------------------------------------------------

class SimonSaysGame:
    def __init__(self, socket_callback=None):
        self.sequence = []
        self.leds = {}
        self.buttons = {}
        self.colors = list(HARDWARE_SETUP.keys())
        self.buzzer = Buzzer(BUZZER_PIN)
        self.socket_callback = socket_callback
        
        self.flash_delay = FLASH_DELAY
        self.sequence_pause = SEQUENCE_PAUSE
        
        self.remote_input_queue = None
        self.game_running = False

        for color, pins in HARDWARE_SETUP.items():
            self.leds[color] = LED(pins["led"])
            self.buttons[color] = Button(pins["btn"])
            
    def _emit(self, event, data):
        if self.socket_callback:
            self.socket_callback(event, data)

    def process_remote_input(self, color):
        """Wird aufgerufen, wenn im Web-Interface geklickt wird"""
        if color in self.colors:
            print(f"INPUT: Web-Klick für {color}")
            self.remote_input_queue = color

    def flash_led(self, color, is_player=False):
        """Lässt LED leuchten und synchronisiert das Web-Interface"""
        # 1. Web: Licht AN
        self._emit('led_state', {'color': color, 'state': 'on'})
        
        # 2. Hardware: AN
        self.leds[color].on()
        self.buzzer.on()
        
        # Zeit abwarten (Spieler-Klicks sind meist kürzer für besseres Gefühl)
        duration = self.flash_delay if not is_player else 0.2
        time.sleep(duration)
        
        # 3. Hardware: AUS
        self.leds[color].off()
        self.buzzer.off()
        
        # 4. Web: Licht AUS
        self._emit('led_state', {'color': color, 'state': 'off'})
        time.sleep(self.sequence_pause)

    def play_sequence(self):
        self._emit('game_status', {'msg': 'Simon zeigt...'})
        time.sleep(0.5)
        for color in self.sequence:
            self.flash_led(color)

    def wait_for_any_button(self):
        self.remote_input_queue = None
        while True:
            # A) Check Hardware (nur wenn vorhanden)
            if IS_HARDWARE:
                for color, btn in self.buttons.items():
                    if btn.is_pressed:
                        while btn.is_pressed: time.sleep(0.01)
                        return color

            # B) Check Web Input (immer aktiv)
            if self.remote_input_queue:
                color = self.remote_input_queue
                self.remote_input_queue = None 
                return color
            
            time.sleep(0.02)

    def get_player_input(self):
        self._emit('game_status', {'msg': 'Du bist dran!'})
        for expected_color in self.sequence:
            pressed_color = self.wait_for_any_button()
            if pressed_color == expected_color:
                self.flash_led(pressed_color, is_player=True)
            else:
                return False
        return True

    def game_over_signal(self):
        score = len(self.sequence)
        self._emit('game_over', {'score': score})
        for _ in range(3):
            self.buzzer.on()
            for led in self.leds.values(): led.on()
            time.sleep(0.3)
            self.buzzer.off()
            for led in self.leds.values(): led.off()
            time.sleep(0.3)

    def wait_for_start_with_wave(self):
        self._emit('game_status', {'msg': 'Warte auf Start...'})
        wave = self.colors + self.colors[::-1]
        self.remote_input_queue = None
        
        while True:
            for color in wave:
                self.leds[color].on()
                # Während die LED am Pi leuchtet, prüfen wir auf Klicks
                start_check = time.time() + 0.15
                while time.time() < start_check:
                    if IS_HARDWARE:
                        for btn in self.buttons.values():
                            if btn.is_pressed: return self._stop_wave()
                    if self.remote_input_queue: return self._stop_wave()
                    time.sleep(0.02)
                self.leds[color].off()

    def _stop_wave(self):
        for l in self.leds.values(): l.off()
        self.remote_input_queue = None
        time.sleep(0.5)

    def start_game_loop(self):
        while True:
            self.wait_for_start_with_wave()
            self.sequence = []
            self.game_running = True
            time.sleep(1)
            while self.game_running:
                self.sequence.append(random.choice(self.colors))
                self.play_sequence()
                if not self.get_player_input():
                    self.game_over_signal()
                    self.game_running = False
                else:
                    time.sleep(0.8)