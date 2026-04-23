import time
import random
import threading
import os
from gpiozero import LED, Button, Buzzer, Device, DigitalOutputDevice, DigitalInputDevice
from gpiozero.exc import BadPinFactory
from gpiozero.pins.mock import MockFactory

# Wir importieren die Konfiguration
from app.config import (
    HARDWARE_SETUP, BUZZER_PIN, FLASH_DELAY, SEQUENCE_PAUSE, 
    IS_RASPI, DIFFICULTY_SETTINGS, DIFFICULTY_BUTTONS,
    SNES_PINS, SNES_MAPPING
)

# Lokaler Mock-Import, falls wir nicht auf dem Pi sind
if not IS_RASPI:
    print("Versuche mock_gpio_gui zu laden...")
    try:
        from mock_gpio_gui import LED, Button, Buzzer, Device, DigitalOutputDevice, DigitalInputDevice
        print("GUI-Emulator geladen.")
    except ImportError as e:
        print(f"Fehler beim Laden von mock_gpio_gui: {e}")
        try:
            Device.pin_factory = MockFactory()
        except:
            pass

class SilentBuzzer:
    def on(self): pass
    def off(self): pass

class SimonSaysGame:
    def __init__(self, socket_callback=None):
        self.sequence = []
        self.leds = {}
        self.buttons = {}
        self.colors = list(HARDWARE_SETUP.keys())
        self.socket_callback = socket_callback

        try:
            self.buzzer = Buzzer(BUZZER_PIN)
        except Exception:
            self.buzzer = SilentBuzzer()
        
        self.flash_delay = FLASH_DELAY
        self.sequence_pause = SEQUENCE_PAUSE
        self.current_difficulty = "medium"
        
        self.remote_inputs = []
        self.remote_input_lock = threading.Lock()
        self.game_running = False
        self.led_states = {color: 'off' for color in self.colors}

        # Hardware initialisieren
        for color, pins in HARDWARE_SETUP.items():
            self.leds[color] = LED(pins["led"])
            self.buttons[color] = Button(pins["btn"], pull_up=True)

        # Difficulty Buttons
        self.diff_btns = []
        for level, pin in DIFFICULTY_BUTTONS.items():
            try:
                btn = Button(pin, pull_up=True)
                btn.when_pressed = lambda l=level: self.set_difficulty(l)
                self.diff_btns.append(btn)
            except: pass

        # SNES Controller
        self.snes_enabled = False
        if IS_RASPI:
            try:
                self.snes_latch = DigitalOutputDevice(SNES_PINS["LATCH"])
                self.snes_clock = DigitalOutputDevice(SNES_PINS["CLOCK"])
                self.snes_data = DigitalInputDevice(SNES_PINS["DATA"], pull_up=True)
                self.snes_enabled = True
                
                # Check for ghosting
                test = self.read_snes_controller()
                if all(b == 0 for b in test):
                    print("SNES Ghosting erkannt -> deaktiviert.")
                    self.snes_enabled = False
            except:
                self.snes_enabled = False

        self.snes_button_names = [
            "B", "Y", "SELECT", "START", "UP", "DOWN", "LEFT", "RIGHT",
            "A", "X", "L", "R", "-", "-", "-", "-"
        ]

        self._print_hardware_report()

    def _print_hardware_report(self):
        print("\n--- SIMON SAYS HW ---")
        print(f"Modus: {'PI' if IS_RASPI else 'MOCK'}")
        print(f"SNES: {'AN' if self.snes_enabled else 'AUS'}")
        print("---------------------\n")

    def _emit(self, event, data):
        if self.socket_callback:
            self.socket_callback(event, data)

    def _set_led_state(self, color, state):
        led_state = 'on' if state else 'off'
        self.led_states[color] = led_state
        if state: self.leds[color].on()
        else: self.leds[color].off()
        self._emit('led_state', {'color': color, 'state': led_state})

    def set_difficulty(self, level):
        """Ändert Schwierigkeit und gibt LED-Feedback (G=Easy, Y=Mid, R=Hard)"""
        if level in DIFFICULTY_SETTINGS:
            print(f"Difficulty set to: {level}")
            cfg = DIFFICULTY_SETTINGS[level]
            self.flash_delay = cfg['flash']
            self.sequence_pause = cfg['pause']
            self.current_difficulty = level
            self._emit('difficulty_changed', {'level': level})
            
            # LED Feedback (Leicht=Grün, Mittel=Gelb, Schwer=Rot)
            fb = {'easy': 'green', 'medium': 'yellow', 'hard': 'red'}.get(level)
            if fb:
                threading.Thread(target=self.flash_led, args=(fb,), daemon=True).start()
            
            if hasattr(self, 'buzzer'):
                try:
                    self.buzzer.on()
                    time.sleep(0.1)
                    self.buzzer.off()
                except: pass

    def read_snes_controller(self):
        if not self.snes_enabled: return [1] * 16
        bits = []
        self.snes_latch.on()
        time.sleep(0.00001)
        self.snes_latch.off()
        for _ in range(16):
            bits.append(0 if self.snes_data.is_active else 1)
            self.snes_clock.on()
            time.sleep(0.00001)
            self.snes_clock.off()
        return bits

    def handle_snes_special_buttons(self):
        """Prüft SELECT (Restart), L/R (Difficulty)"""
        if not self.snes_enabled: return
        pressed = []
        bits = self.read_snes_controller()
        for i, bit in enumerate(bits):
            if bit == 0 and i < len(self.snes_button_names):
                pressed.append(self.snes_button_names[i])
        
        if len(pressed) > 10: return # Ghosting

        # 1. SELECT -> RESTART
        if "SELECT" in pressed:
            print("RESTART über SNES SELECT")
            self.game_running = False
            return True

        # 2. L/R -> DIFFICULTY
        if "L" in pressed:
            levels = ['easy', 'medium', 'hard']
            curr_idx = levels.index(self.current_difficulty)
            new_idx = max(0, curr_idx - 1)
            self.set_difficulty(levels[new_idx])
            while "L" in self.read_pressed_snes_buttons(): time.sleep(0.01) # Debounce
        
        if "R" in pressed:
            levels = ['easy', 'medium', 'hard']
            curr_idx = levels.index(self.current_difficulty)
            new_idx = min(2, curr_idx + 1)
            self.set_difficulty(levels[new_idx])
            while "R" in self.read_pressed_snes_buttons(): time.sleep(0.01) # Debounce
            
        return False

    def read_pressed_snes_buttons(self):
        if not self.snes_enabled: return []
        bits = self.read_snes_controller()
        pressed = []
        for i, bit in enumerate(bits):
            if bit == 0 and i < len(self.snes_button_names):
                name = self.snes_button_names[i]
                if name != "-": pressed.append(name)
        if len(pressed) > 10: return []
        return pressed

    def process_remote_input(self, color):
        if color in self.colors or color == "START_SIGNAL":
            with self.remote_input_lock:
                self.remote_inputs.append(color)

    def _pop_remote_input(self):
        with self.remote_input_lock:
            return self.remote_inputs.pop(0) if self.remote_inputs else None

    def _clear_remote_inputs(self):
        with self.remote_input_lock:
            self.remote_inputs.clear()

    def flash_led(self, color):
        self._set_led_state(color, True)
        if hasattr(self, 'buzzer'):
            try: self.buzzer.on()
            except: pass
        time.sleep(self.flash_delay)
        self._set_led_state(color, False)
        if hasattr(self, 'buzzer'):
            try: self.buzzer.off()
            except: pass
        time.sleep(self.sequence_pause)

    def play_sequence(self):
        self._emit('game_status', {'msg': 'Simon zeigt...'})
        time.sleep(0.8)
        for color in self.sequence:
            # Check for RESTART during Simon phase
            if self.handle_snes_special_buttons(): return
            self.flash_led(color)

    def wait_for_any_button(self):
        while True:
            # Special SNES Buttons (SELECT/L/R)
            if self.handle_snes_special_buttons():
                return "RESTART_SIGNAL"

            # A) Hardware
            for color, btn in self.buttons.items():
                if btn.is_pressed:
                    self._set_led_state(color, True)
                    if hasattr(self, 'buzzer'):
                        try: self.buzzer.on()
                        except: pass
                    while btn.is_pressed: time.sleep(0.01)
                    self._set_led_state(color, False)
                    if hasattr(self, 'buzzer'):
                        try: self.buzzer.off()
                        except: pass
                    return color
            # B) Web
            color = self._pop_remote_input()
            if color in self.colors:
                self.flash_led(color)
                return color
            # C) SNES Game Buttons
            snes_btn = self.read_pressed_snes_buttons()
            if snes_btn:
                for b in snes_btn:
                    if b in SNES_MAPPING:
                        target = SNES_MAPPING[b]
                        self._set_led_state(target, True)
                        while b in self.read_pressed_snes_buttons(): time.sleep(0.01)
                        self._set_led_state(target, False)
                        return target
            time.sleep(0.01)

    def get_player_input(self):
        self._emit('game_status', {'msg': 'Du bist dran!'})
        self._clear_remote_inputs()
        for expected in self.sequence:
            pressed = self.wait_for_any_button()
            if pressed == "RESTART_SIGNAL": return "RESTART"
            if pressed != expected:
                return False
        return True

    def game_over_signal(self):
        score = max(0, len(self.sequence) - 1)
        self._emit('game_over', {'score': score})
        for _ in range(3):
            for c in self.colors: self._set_led_state(c, True)
            time.sleep(0.2)
            for c in self.colors: self._set_led_state(c, False)
            time.sleep(0.2)
        self.wait_for_name_input(score)

    def wait_for_name_input(self, score):
        self._emit('request_name', {'score': score})
        self.name_received_flag = False
        timer = 300
        while not self.name_received_flag and timer > 0:
            for btn in self.buttons.values():
                if btn.is_pressed:
                    self.name_received_flag = True
                    return
            if self.handle_snes_special_buttons():
                self.name_received_flag = True
                return
            time.sleep(0.1)
            timer -= 1

    def on_name_submitted(self, name):
        if getattr(self, 'name_received_flag', False): return
        self.name_received_flag = True
        from app.repository import add_highscore
        try: add_highscore(name, getattr(self, 'current_score', 0))
        except: pass

    def wait_for_start_with_wave(self):
        self._emit('game_status', {'msg': 'Starten?'})
        wave = self.colors + self.colors[-2:0:-1]
        self._clear_remote_inputs()
        while True:
            for color in wave:
                self._set_led_state(color, True)
                end = time.time() + 0.15
                while time.time() < end:
                    if self.handle_snes_special_buttons(): pass # Update diffs
                    for c, btn in self.buttons.items():
                        if btn.is_pressed:
                            self._set_led_state(color, False); return
                    if self._pop_remote_input():
                        self._set_led_state(color, False); return
                    if self.read_pressed_snes_buttons():
                        self._set_led_state(color, False); return
                    time.sleep(0.01)
                self._set_led_state(color, False)

    def start_game_loop(self):
        while True:
            self.wait_for_start_with_wave()
            self.sequence = []
            self.game_running = True
            self._emit('game_status', {'msg': 'GO!'})
            time.sleep(0.8)
            while self.game_running:
                self.sequence.append(random.choice(self.colors))
                self.play_sequence()
                if not self.game_running: break # Restart signaled during playback
                res = self.get_player_input()
                if res == "RESTART": 
                    self.game_running = False
                elif not res:
                    self.game_over_signal()
                    self.game_running = False
                else:
                    time.sleep(0.4)

    def get_debug_status(self):
        return {
            'leds': self.led_states,
            'buttons': {c: ('pressed' if b.is_pressed else 'released') for c, b in self.buttons.items()},
            'snes_enabled': self.snes_enabled,
            'diff': self.current_difficulty
        }

    def toggle_led_debug(self, color):
        if color in self.leds:
            s = not (self.led_states[color] == 'on')
            self._set_led_state(color, s)
            return s
        return False
