import time
import random
import threading
from gpiozero import LED, Button, Buzzer

# Wir importieren die Konfiguration
from app.config import HARDWARE_SETUP, BUZZER_PIN, FLASH_DELAY, SEQUENCE_PAUSE

class SimonSaysGame:
    def __init__(self, socket_callback=None):
        """
        socket_callback: Funktion, um Daten an das Web-Frontend zu senden.
        """
        self.sequence = []
        self.leds = {}
        self.buttons = {}
        self.colors = list(HARDWARE_SETUP.keys())
        self.buzzer = Buzzer(BUZZER_PIN)
        self.socket_callback = socket_callback
        
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
            
    def _emit(self, event, data):
        """Hilfsfunktion sendet Daten an Flask"""
        if self.socket_callback:
            self.socket_callback(event, data)

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
