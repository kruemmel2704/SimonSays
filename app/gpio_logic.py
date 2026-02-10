import time
import random
import threading
from gpiozero import LED, Button, Buzzer
# Wir importieren die Konfiguration aus deinem app-Ordner
from app.config import HARDWARE_SETUP, BUZZER_PIN, FLASH_DELAY, SEQUENCE_PAUSE

class SimonSaysGame:
    def __init__(self, socket_callback=None):
        """
        socket_callback: Eine Funktion, die aufgerufen wird, um Events 
        an das Web-Frontend zu senden.
        """
        self.sequence = []
        self.leds = {}
        self.buttons = {}
        self.colors = list(HARDWARE_SETUP.keys())
        self.buzzer = Buzzer(BUZZER_PIN)
        self.socket_callback = socket_callback
        
        # Schwierigkeitseinstellungen (können über Flask geändert werden)
        self.flash_delay = FLASH_DELAY
        self.sequence_pause = SEQUENCE_PAUSE
        
        # Hardware Initialisierung
        for color, pins in HARDWARE_SETUP.items():
            self.leds[color] = LED(pins["led"])
            self.buttons[color] = Button(pins["btn"])

    def _emit_event(self, event, data):
        """Hilfsmethode, um Events an Flask zu melden."""
        if self.socket_callback:
            self.socket_callback(event, data)

    def beep(self, times, speed=0.1):
        for _ in range(times):
            self.buzzer.on()
            time.sleep(speed)
            self.buzzer.off()
            if times > 1:
                time.sleep(speed)

    def flash_led(self, color, is_simon=True):
        """Leuchtet eine LED und sendet ein Signal an den Browser."""
        # Signal an Web-Interface: LED AN
        self._emit_event('led_state', {'color': color, 'state': 'on', 'who': 'simon' if is_simon else 'player'})
        
        self.leds[color].on()
        self.buzzer.on()
        time.sleep(self.flash_delay)
        self.leds[color].off()
        self.buzzer.off()
        
        # Signal an Web-Interface: LED AUS
        self._emit_event('led_state', {'color': color, 'state': 'off'})
        time.sleep(self.sequence_pause)

    def play_sequence(self):
        self._emit_event('game_status', {'msg': 'Simon zeigt...'})
        self.beep(1, 0.2)
        time.sleep(0.5)
        for color in self.sequence:
            self.flash_led(color, is_simon=True)

    def handle_web_input(self, color):
    # Speichere den Web-Klick in einer Variable, die wait_for_any_button prüft
        self.last_web_click = color

    def wait_for_any_button(self):
        self.last_web_click = None
        while True:
            # 1. Physische Buttons prüfen
            for color, btn in self.buttons.items():
                if btn.is_pressed:
                    while btn.is_pressed: time.sleep(0.01)
                    return color
        
            # 2. Web-Klicks prüfen
                if self.last_web_click:
                    color = self.last_web_click
                    self.last_web_click = None
                    return color
            
        time.sleep(0.01)

    def get_player_input(self):
        self._emit_event('game_status', {'msg': 'Du bist dran!'})
        self.beep(2, 0.05)
        for expected_color in self.sequence:
            pressed_color = self.wait_for_any_button()
            if pressed_color == expected_color:
                self.flash_led(pressed_color, is_simon=False)
            else:
                return False
        return True

    def game_over_signal(self):
        score = len(self.sequence) - 1
        self._emit_event('game_over', {'score': score})
        self.beep(3, 0.5)
        for _ in range(3):
            for led in self.leds.values(): led.on()
            time.sleep(0.2)
            for led in self.leds.values(): led.off()
            time.sleep(0.2)

    def wait_for_start_with_wave(self):
        self._emit_event('game_status', {'msg': 'Warte auf Start...'})
        wave_pattern = self.colors + self.colors[-2:0:-1]
        button_pressed = False
        while not button_pressed:
            for color in wave_pattern:
                self.leds[color].on()
                # Kurzer Check auf Input
                start_time = time.time()
                while time.time() - start_time < 0.1:
                    for btn in self.buttons.values():
                        if btn.is_pressed:
                            button_pressed = True
                            for l in self.leds.values(): l.off()
                            self.beep(1, 0.2)
                            return
                    time.sleep(0.01)
                self.leds[color].off()

    def start_game_loop(self):
        """Die Hauptschleife, die im Hintergrund-Thread läuft."""
        while True:
            self.wait_for_start_with_wave()
            self.sequence = []
            active = True
            while active:
                self.sequence.append(random.choice(self.colors))
                self.play_sequence()
                if not self.get_player_input():
                    self.game_over_signal()
                    active = False
                    time.sleep(1)
                else:
                    time.sleep(0.8)