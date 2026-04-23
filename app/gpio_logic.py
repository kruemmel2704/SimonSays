import time
import random
import threading
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
        print("Fallback auf Standard-Mock (ohne GUI)...")
        # Wir setzen die Factory SOFORT, damit gpiozero beim Initialisieren von LEDs nicht abstürzt
        try:
            Device.pin_factory = MockFactory()
        except Exception:
            pass


class SilentBuzzer:
    """Fallback-Buzzer für Umgebungen ohne echte GPIO-Hardware."""
    def on(self):
        pass

    def off(self):
        pass

class SimonSaysGame:
    def __init__(self, socket_callback=None):
        """
        socket_callback: Funktion, um Daten an das Web-Frontend zu senden.
        """
        # Factory ist schon global gesetzt


        self.sequence = []
        self.leds = {}
        self.buttons = {}
        self.colors = list(HARDWARE_SETUP.keys())
        self.socket_callback = socket_callback

        try:
            self.buzzer = Buzzer(BUZZER_PIN)
        except Exception:
            self.buzzer = SilentBuzzer()
        
        # Einstellungen
        self.flash_delay = FLASH_DELAY
        self.sequence_pause = SEQUENCE_PAUSE
        self.current_difficulty = "medium"
        
        # Eingaben kommen aus Flask-Socket-Threads und werden vom Game-Thread gelesen.
        self.remote_inputs = []
        self.remote_input_lock = threading.Lock()
        self.game_running = False
        self.led_states = {color: 'off' for color in self.colors}

        # Hardware initialisieren
        for color, pins in HARDWARE_SETUP.items():
            self.leds[color] = LED(pins["led"])
            self.buttons[color] = Button(pins["btn"])

        # Difficulty Buttons
        self.diff_btns = [] # Keep references
        for level, pin in DIFFICULTY_BUTTONS.items():
            try:
                btn = Button(pin)
                btn.when_pressed = lambda l=level: self.set_difficulty(l)
                self.diff_btns.append(btn)
            except Exception as e:
                print(f"Fehler bei Difficulty Button {level} (Pin {pin}): {e}")

        # SNES Controller
        try:
            self.snes_latch = DigitalOutputDevice(SNES_PINS["LATCH"])
            self.snes_clock = DigitalOutputDevice(SNES_PINS["CLOCK"])
            self.snes_data = DigitalInputDevice(SNES_PINS["DATA"], pull_up=True)
            self.snes_enabled = True
        except Exception as e:
            print(f"SNES Controller konnte nicht initialisiert werden: {e}")
            self.snes_enabled = False

        self.snes_button_names = [
            "B", "Y", "SELECT", "START", "UP", "DOWN", "LEFT", "RIGHT",
            "A", "X", "L", "R", "-", "-", "-", "-"
        ]

        self._print_hardware_report()

    def _print_hardware_report(self):
        """Gibt eine Übersicht der Hardware-Initialisierung aus."""
        print("\n--- SIMON SAYS HARDWARE REPORT ---")
        print(f"Modus: {'RASPBERRY PI' if IS_RASPI else 'EMULATOR/MOCK'}")
        
        print("\nLEDs & Buttons:")
        for color, pins in HARDWARE_SETUP.items():
            led_ok = "OK" if self.leds.get(color) else "FAIL"
            btn_ok = "OK" if self.buttons.get(color) else "FAIL"
            print(f"  - {color.upper():7}: LED (Pin {pins['led']}) [{led_ok}], Button (Pin {pins['btn']}) [{btn_ok}]")
            
        print("\nSNES Controller:")
        if self.snes_enabled:
            print(f"  - LATCH: Pin {SNES_PINS['LATCH']} [OK]")
            print(f"  - CLOCK: Pin {SNES_PINS['CLOCK']} [OK]")
            print(f"  - DATA : Pin {SNES_PINS['DATA']}  [OK]")
        else:
            print("  - Status: DEAKTIVIERT oder FEHLER")
            
        print("\nSonstiges:")
        print(f"  - Buzzer: Pin {BUZZER_PIN} [{'OK' if hasattr(self, 'buzzer') else 'FAIL'}]")
        print(f"  - Difficulty Buttons: {len(self.diff_btns)} initialisiert")
        print("----------------------------------\n")

    def _emit(self, event, data):
        """Hilfsfunktion sendet Daten an Flask"""
        # print(f"Logic: _emit {event}") 
        if self.socket_callback:
            self.socket_callback(event, data)
        else:
            print(f"ERROR: _emit '{event}' called but socket_callback is None!")

    def _set_led_state(self, color, state):
        """Setzt Hardware-LED und spiegelt den Zustand ins Web-Frontend."""
        led_state = 'on' if state else 'off'
        self.led_states[color] = led_state
        if state:
            self.leds[color].on()
        else:
            self.leds[color].off()
        self._emit('led_state', {'color': color, 'state': led_state})

    def get_led_snapshot(self):
        """Liefert den aktuell bekannten LED-Zustand für neue Clients."""
        return dict(self.led_states)

    def set_difficulty(self, level):
        """Ändert den Schwierigkeitsgrad via Hardware-Button"""
        if level in DIFFICULTY_SETTINGS:
            print(f"Difficulty changed to: {level}")
            cfg = DIFFICULTY_SETTINGS[level]
            self.flash_delay = cfg['flash']
            self.sequence_pause = cfg['pause']
            self.current_difficulty = level
            
            # Feedback ans Frontend
            self._emit('difficulty_changed', {'level': level})
            
            # Akustisches Feedback
            if hasattr(self, 'buzzer'):
                try:
                    # Kurzer Bip
                    self.buzzer.on()
                    time.sleep(0.1)
                    self.buzzer.off()
                except:
                    pass

    # --- SNES CONTROLLER LOGIK ---
    def read_snes_controller(self):
        """Liest die 16 Bits vom SNES Controller ein."""
        if not self.snes_enabled:
            return [1] * 16 # Alles ungedrückt (High bei PUD_UP)

        bits = []
        # Latch Puls
        self.snes_latch.on()
        time.sleep(0.00002)
        self.snes_latch.off()
        time.sleep(0.00002)

        # 16 Bits schieben
        for _ in range(16):
            bits.append(1 if self.snes_data.is_active else 0)
            self.snes_clock.on()
            time.sleep(0.00002)
            self.snes_clock.off()
            time.sleep(0.00002)
        
        return bits

    def read_pressed_snes_buttons(self):
        """Gibt eine Liste der aktuell gedrückten SNES-Button-Namen zurück."""
        bits = self.read_snes_controller()
        pressed = []
        for i, bit in enumerate(bits):
            if i < len(self.snes_button_names):
                name = self.snes_button_names[i]
                if name != "-" and bit == 0:
                    pressed.append(name)
        return pressed

    # --- SCHNITTSTELLE ZUM WEB (WICHTIG!) ---
    def process_remote_input(self, color):
        """Wird von remote.py aufgerufen, wenn jemand im Browser klickt."""
        if color in self.colors or color == "START_SIGNAL":
            print(f"Game-Logik empfängt Web-Input: {color}")
            with self.remote_input_lock:
                self.remote_inputs.append(color)
        else:
            print(f"Ignoriere unbekannte Farbe: {color}")

    def _pop_remote_input(self):
        with self.remote_input_lock:
            if not self.remote_inputs:
                return None
            return self.remote_inputs.pop(0)

    def _clear_remote_inputs(self):
        with self.remote_input_lock:
            self.remote_inputs.clear()

    # --- HARDWARE STEUERUNG ---
    def flash_led(self, color):
        """Lässt LED leuchten und synchronisiert das Web-Frontend"""
        # 1. Hardware + Web: LICHT AN
        self._set_led_state(color, True)
        # Sicherstellen, dass der Buzzer nur genutzt wird, wenn er initialisiert wurde
        if hasattr(self, 'buzzer'):
            try:
                self.buzzer.on()
            except:
                pass
        
        time.sleep(self.flash_delay)
        
        # 2. Hardware aus
        self._set_led_state(color, False)
        if hasattr(self, 'buzzer'):
            try:
                self.buzzer.off()
            except:
                pass

        time.sleep(self.sequence_pause)

    def play_sequence(self):
        """Spielt die aktuelle Folge ab"""
        self._emit('game_status', {'msg': 'Simon zeigt...'})
        time.sleep(1)
        for color in self.sequence:
            self.flash_led(color)

    def wait_for_any_button(self):
        """
        Wartet auf Hardware-Button, Web-Input ODER SNES-Controller.
        Gibt die Farbe zurück, sobald die Taste GEDRÜCKT wurde.
        """
        while True:
            # A) Check Hardware Buttons
            for color, btn in self.buttons.items():
                if btn.is_pressed:
                    # Sofort Licht an zur Bestätigung
                    self._set_led_state(color, True)
                    if hasattr(self, 'buzzer'):
                        try: self.buzzer.on()
                        except: pass
                    
                    # Warten bis losgelassen
                    while btn.is_pressed:
                        time.sleep(0.01)
                    
                    # Licht aus
                    self._set_led_state(color, False)
                    if hasattr(self, 'buzzer'):
                        try: self.buzzer.off()
                        except: pass
                        
                    return color

            # B) Check Web Input
            color = self._pop_remote_input()
            if color in self.colors:
                # Bei Web-Input simulieren wir das Drücken kurz
                self.flash_led(color)
                return color
            
            # C) Check SNES Controller
            snes_pressed = self.read_pressed_snes_buttons()
            for snes_btn in snes_pressed:
                if snes_btn in SNES_MAPPING:
                    target = SNES_MAPPING[snes_btn]
                    if target in self.colors:
                        self._set_led_state(target, True)
                        while snes_btn in self.read_pressed_snes_buttons():
                            time.sleep(0.01)
                        self._set_led_state(target, False)
                        return target
            
            time.sleep(0.01)

    def get_player_input(self):
        """Prüft die Eingabe des Spielers"""
        self._emit('game_status', {'msg': 'Du bist dran!'})
        
        # Sicherstellen, dass keine "alten" Clicks von der Simon-Phase mehr im Speicher sind
        self._clear_remote_inputs()
        
        for expected_color in self.sequence:
            # Warten auf Eingabe (Licht-Feedback passiert jetzt direkt in wait_for_any_button)
            pressed_color = self.wait_for_any_button()
            
            if pressed_color != expected_color:
                # Falsch: Game Over
                return False
                
        return True

    def game_over_signal(self):
        """Spielende Animation"""
        # Korrekter Score: Die Anzahl der erfolgreich wiederholten Runden
        score = max(0, len(self.sequence) - 1)
        print(f"Game Over. Erreichter Score: {score}")
        self._emit('game_over', {'score': score})
        
        # 3x Blinken und Piepen
        for _ in range(3):
            if hasattr(self, 'buzzer'):
                try: self.buzzer.on()
                except: pass
            for color in self.colors:
                self._set_led_state(color, True)
            time.sleep(0.3)
            if hasattr(self, 'buzzer'):
                try: self.buzzer.off()
                except: pass
            for color in self.colors:
                self._set_led_state(color, False)
            time.sleep(0.3)

        # Warten auf Namenseingabe ODER Hardware-Restart
        self.wait_for_name_input(score)

    def wait_for_name_input(self, score):
        """
        Wartet auf Namen vom Web-Dashboard. 
        Kann durch Drücken einer Hardware-Taste abgebrochen werden (Sofort-Restart).
        """
        self._emit('request_name', {'score': score})
        self.name_received_flag = False
        self.current_score = score
        
        timeout_loops = 300 # 30 Sekunden maximal warten
        while not self.name_received_flag and timeout_loops > 0:
            # Prüfen ob jemand an der Hardware eine Taste drückt zum Weiterspielen
            for btn in self.buttons.values():
                if btn.is_pressed:
                    print("Hardware-Restart erkannt.")
                    self.name_received_flag = True
                    return # Sofort zurück zum Start-Wave
            
            # SNES Start?
            if self.read_pressed_snes_buttons():
                self.name_received_flag = True
                return

            time.sleep(0.1)
            timeout_loops -= 1
            
        print("Name-Phase beendet.")

    def on_name_submitted(self, name):
        """
        Wird von der Flask-Route aufgerufen, wenn ein Name kommt.
        """
        # Verhindere doppelte Verarbeitung (Race Condition oder mehrfacher Client-Emit)
        if self.name_received_flag:
            print(f"Name '{name}' ignoriert, da Spiel bereits fortgesetzt wird.")
            return

        print(f"Name erhalten: {name} für Score: {self.current_score}")
        
        # In die DB speichern (im App Context)
        # from app import db
        # from app.models import Highscore
        from app.repository import add_highscore
        # from flask import current_app

        # Workaround: Da wir hier im Thread sind, müssen wir sicherstellen, dass wir einen App Context haben
        # Meistens wird diese Funktion aber vom Main-Thread (Flask Request) aufgerufen, da passt es.
        # Falls es vom Socket-Thread kommt, ist auch ein Context da.
        
        try:
            # hs = Highscore(name=name, score=self.current_score)
            # db.session.add(hs)
            # db.session.commit()
            add_highscore(name, self.current_score)
            print("Highscore gespeichert.")
            
            # Frontend aktualisieren
            from app.routes.main import handle_request_highscores
            handle_request_highscores()
            
        except Exception as e:
            print(f"Fehler beim Speichern des Highscores: {e}")

        # Loop freigeben
        self.name_received_flag = True

    def wait_for_start_with_wave(self):
        """Warte-Animation bis jemand drückt (Start)"""
        self._emit('game_status', {'msg': 'Drücke eine Taste zum Starten'})
        wave = self.colors + self.colors[-2:0:-1]
        
        self._clear_remote_inputs()
        
        while True:
            for color in wave:
                self._set_led_state(color, True)
                
                # Kurze Pause, in der wir auf Start-Signale prüfen
                end_time = time.time() + 0.1
                while time.time() < end_time:
                    # 1. Hardware Start?
                    for btn in self.buttons.values():
                        if btn.is_pressed:
                            for wave_color in self.colors:
                                self._set_led_state(wave_color, False)
                            time.sleep(0.5)
                            return
                    
                    # 2. Web Start?
                    if self._pop_remote_input():
                        for wave_color in self.colors:
                            self._set_led_state(wave_color, False)
                        time.sleep(0.5)
                        return
                    
                    # 3. SNES Start?
                    snes_pressed = self.read_pressed_snes_buttons()
                    if snes_pressed:
                        # Jede Taste am SNES startet das Spiel
                        for wave_color in self.colors:
                            self._set_led_state(wave_color, False)
                        time.sleep(0.5)
                        return
                    
                    time.sleep(0.01)
                
                self._set_led_state(color, False)

    def start_game_loop(self):
        """Die Hauptschleife (läuft im Hintergrund-Thread)"""
        print("Hardware-Thread gestartet...")
        while True:
            # 1. Warten auf Start
            self.wait_for_start_with_wave()
            
            # 2. Spiel beginnt
            self.sequence = []
            self.game_running = True
            self._emit('game_status', {'msg': 'Spiel startet!'})
            time.sleep(1)

            while self.game_running:
                # Neue Farbe dazu
                self.sequence.append(random.choice(self.colors))
                
                # Simon zeigt
                self.play_sequence()
                
                # Spieler ist dran
                if not self.get_player_input():
                    self.game_over_signal()
                    self.game_running = False
                else:
                    time.sleep(0.5)
    def get_debug_status(self):
        """Liefert den aktuellen Status aller Hardware-Komponenten für Debug-Zwecke."""
        status = {
            'leds': {color: self.led_states[color] for color in self.colors},
            'buttons': {color: ('pressed' if self.buttons[color].is_pressed else 'released') for color in self.colors},
            'snes': self.read_pressed_snes_buttons(),
            'difficulty': self.current_difficulty,
            'is_raspi': IS_RASPI
        }
        return status

    def toggle_led_debug(self, color):
        """Schaltet eine LED für Debug-Zwecke um (unabhängig vom Spiel-Loop)."""
        if color in self.leds:
            current = self.led_states[color] == 'on'
            new_state = not current
            self._set_led_state(color, new_state)
            return new_state
        return False
