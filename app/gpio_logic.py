import time
import random
import threading
from gpiozero import LED, Button, Buzzer, Device
from gpiozero.exc import BadPinFactory
from gpiozero.pins.mock import MockFactory

# Wir importieren die Konfiguration
from app.config import HARDWARE_SETUP, BUZZER_PIN, FLASH_DELAY, SEQUENCE_PAUSE, IS_RASPI, DIFFICULTY_SETTINGS, DIFFICULTY_BUTTONS

# Lokaler Mock-Import, falls wir nicht auf dem Pi sind
if not IS_RASPI:
    print("Versuche mock_gpio_gui zu laden...")
    try:
        from mock_gpio_gui import LED, Button, Buzzer, Device
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
        
        # WICHTIG: Hier speichern wir Web-Klicks zwischen
        self.remote_input_queue = None
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
                # Lambda with default arg to capture the current level value
                btn.when_pressed = lambda l=level: self.set_difficulty(l)
                self.diff_btns.append(btn)
            except Exception as e:
                print(f"Fehler bei Difficulty Button {level} (Pin {pin}): {e}")
            
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

    # --- SCHNITTSTELLE ZUM WEB (WICHTIG!) ---
    def process_remote_input(self, color):
        """Wird von remote.py aufgerufen, wenn jemand im Browser klickt"""
        if color in self.colors:
            print(f"Game-Logik empfängt Web-Input: {color}")
            self.remote_input_queue = color
        else:
            print(f"Ignoriere unbekannte Farbe: {color}")

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
        Der Kern der Hybrid-Steuerung:
        Wartet auf Hardware-Button ODER Web-Input.
        """
        # Queue leeren vor neuer Eingabe
        self.remote_input_queue = None
        
        while True:
            # A) Check Hardware Buttons
            for color, btn in self.buttons.items():
                if btn.is_pressed:
                    # Entprellen (warten bis losgelassen)
                    while btn.is_pressed:
                        time.sleep(0.01)
                    return color

            # B) Check Web Input
            if self.remote_input_queue:
                color = self.remote_input_queue
                self.remote_input_queue = None # Reset
                return color
            
            # CPU schonen
            time.sleep(0.01)

    def get_player_input(self):
        """Prüft die Eingabe des Spielers"""
        self._emit('game_status', {'msg': 'Du bist dran!'})
        
        for expected_color in self.sequence:
            # Warten auf Eingabe (Egal ob Web oder Button)
            pressed_color = self.wait_for_any_button()
            
            if pressed_color == expected_color:
                # Richtig: Feedback geben (LED leuchtet kurz)
                self.flash_led(pressed_color)
            else:
                # Falsch: Game Over
                return False
        return True

    def game_over_signal(self):
        """Spielende Animation"""
        score = len(self.sequence)
        print(f"Game Over. Score: {score}")
        self._emit('game_over', {'score': score})
        
        # 3x Blinken und Piepen
        for _ in range(3):
            self.buzzer.on()
            for color in self.colors:
                self._set_led_state(color, True)
            time.sleep(0.3)
            self.buzzer.off()
            for color in self.colors:
                self._set_led_state(color, False)
            time.sleep(0.3)

        # Warten auf Namenseingabe im Dashboard
        self.wait_for_name_input(score)

    def wait_for_name_input(self, score):
        """
        Blockiert den Game-Loop, bis ein Name über das Dashboard eingegeben wurde.
        """
        self._emit('request_name', {'score': score})
        print("Warte auf Namenseingabe...")
        
        self.name_received_flag = False
        self.current_score = score # Speichern für on_name_submitted
        
        while not self.name_received_flag:
            time.sleep(1.0)
            # Erneut anfordern falls Client neu lädt oder das erste Event verpasst hat
            self._emit('request_name', {'score': score})
            
        print("Name empfangen, Spiel wird zurückgesetzt.")

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
        
        self.remote_input_queue = None # Reset
        
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
                    if self.remote_input_queue:
                        self.remote_input_queue = None
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
