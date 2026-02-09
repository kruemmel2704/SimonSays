import time
import random

# gpiozero vereinfacht die Arbeit mit GPIO (LED, Button, Buzzer) auf dem Raspberry Pi
from gpiozero import LED, Button, Buzzer

# Konfigurationswerte (Pin-Belegung + Timings) sind ausgelagert in Config.py
# Erwartete Struktur (Beispiel):
# HARDWARE_SETUP = {"rot": {"led": 17, "btn": 22}, "gruen": {"led": 27, "btn": 23}, ...}
# BUZZER_PIN = 24
# FLASH_DELAY = 0.3
# SEQUENCE_PAUSE = 0.15
from app.templates.Config import HARDWARE_SETUP, BUZZER_PIN, FLASH_DELAY, SEQUENCE_PAUSE

# Flask ist importiert, wird hier aber (noch) nicht sinnvoll genutzt.
# Hinweis: Ein @app.route("/") ohne Funktion darunter ist syntaktisch/funktional falsch.
# Ich kommentiere das nur, ändere aber keine Logik deiner Game-Klasse.
from flask import Flask

app = Flask("SimonSaysGame")

# Achtung: Dieser Decorator ist so nicht korrekt, weil danach keine Funktion folgt.
# Wenn du Flask wirklich nutzen willst, müsste hier eine Funktion stehen.
@app.route("/")


class SimonSaysGame:
    def __init__(self):
        # Die zu merkende Folge (Liste von Farb-Namen wie "rot", "gruen", ...)
        self.sequence = []

        # Dicts, um LEDs/Buttons nach Farbe zu referenzieren:
        # self.leds["rot"] -> LED-Objekt, self.buttons["rot"] -> Button-Objekt
        self.leds = {}
        self.buttons = {}

        # Farben ergeben sich aus den Keys aus HARDWARE_SETUP (z.B. ["rot","gruen","gelb","blau"])
        self.colors = list(HARDWARE_SETUP.keys())

        # Buzzer am konfigurierten Pin
        self.buzzer = Buzzer(BUZZER_PIN)

        # Hardware initialisieren: pro Farbe eine LED + ein Button
        for color, pins in HARDWARE_SETUP.items():
            self.leds[color] = LED(pins["led"])
            self.buttons[color] = Button(pins["btn"])

    def beep(self, times, speed=0.1):
        """
        Lässt den Buzzer 'times' mal piepen.
        speed = Dauer pro ON/OFF-Phase (Sekunden).
        - times=1, speed=0.2 -> ein längerer Bestätigungston
        - times=2, speed=0.05 -> zwei schnelle Signaltöne
        - times=3, speed=0.5 -> drei langsame Game-Over-Töne
        """
        for _ in range(times):
            self.buzzer.on()
            time.sleep(speed)
            self.buzzer.off()
            # Zwischenpausen nur, wenn mehr als 1 Piep gewünscht ist
            if times > 1:
                time.sleep(speed)

    def wait_for_start_with_wave(self):
        """
        Wartet auf Start: es läuft ein LED-"Wave" (Hin- und Herlauf).
        Sobald irgendein Button gedrückt wird, wird die Animation beendet
        und mit einem Bestätigungston gestartet.
        """
        # Wave-Pattern: Farben vorwärts + rückwärts ohne die Endpunkte doppelt
        # Beispiel bei 4 Farben: [c1,c2,c3,c4] + [c3,c2,c1]
        wave_pattern = self.colors + self.colors[-2:0:-1]

        button_pressed = False
        while not button_pressed:
            for color in wave_pattern:
                # aktuelle Wave-LED an
                self.leds[color].on()

                # für eine kurze Zeit (0.1s) checken wir schnell, ob jemand drückt
                start_time = time.time()
                while time.time() - start_time < 0.1:
                    # Wenn irgendein Button gedrückt ist -> Start
                    for btn in self.buttons.values():
                        if btn.is_pressed:
                            button_pressed = True

                            # alle LEDs aus (Wave sofort stoppen)
                            for l in self.leds.values():
                                l.off()

                            # kurzer Bestätigungston
                            self.beep(1, 0.2)
                            return

                    # kleines Sleep, um CPU nicht unnötig zu belasten
                    time.sleep(0.01)

                # Wave-LED wieder aus
                self.leds[color].off()

    def flash_led(self, color):
        """
        Zeigt eine einzelne Farbe:
        - LED an + Buzzer an für FLASH_DELAY Sekunden
        - danach LED+Buzzer aus
        - anschließend kurze Pause (SEQUENCE_PAUSE), damit man einzelne Schritte gut unterscheidet
        """
        self.leds[color].on()
        self.buzzer.on()  # kurzer Piep während die LED leuchtet
        time.sleep(FLASH_DELAY)
        self.leds[color].off()
        self.buzzer.off()
        time.sleep(SEQUENCE_PAUSE)

    def play_sequence(self):
        """
        Simon zeigt die aktuelle Folge an:
        - 1x Piepen als "Achtung, gleich kommt die Folge"
        - kleine Pause
        - jede Farbe der Folge wird nacheinander geflasht
        """
        self.beep(1, 0.2)
        time.sleep(0.5)
        for color in self.sequence:
            self.flash_led(color)

    def get_player_input(self):
        """
        Spieler gibt die Folge ein:
        - 2x schnelles Piepen als "Du bist dran"
        - dann muss für jeden Schritt der Folge ein Button gedrückt werden
        - korrekt: LED+Buzzer feedback über flash_led()
        - falsch: sofort False (Game Over)
        """
        self.beep(2, 0.05)

        for expected_color in self.sequence:
            pressed_color = self.wait_for_any_button()

            if pressed_color == expected_color:
                # korrekt gedrückt: Feedback (LED + kurzer Ton)
                self.flash_led(pressed_color)
            else:
                # falsche Taste: Runde verloren
                return False

        # komplette Folge korrekt eingegeben
        return True

    def wait_for_any_button(self):
        """
        Blockiert, bis irgendein Button gedrückt und wieder losgelassen wurde.
        Rückgabe: der Farbname (Key), dessen Button gedrückt wurde.
        """
        while True:
            for color, btn in self.buttons.items():
                if btn.is_pressed:
                    # warten bis losgelassen (Debounce/Mehrfachtrigger vermeiden)
                    while btn.is_pressed:
                        time.sleep(0.01)
                    return color

            # CPU entlasten
            time.sleep(0.01)

    def game_over_signal(self):
        """
        Game-Over-Feedback:
        - Ausgabe in Konsole
        - 3x langsamer Ton
        - 3x alle LEDs kurz blinken (visuelles "Ende")
        """
        print("Game Over!")

        # 3x langsam piepen
        self.beep(3, 0.5)

        # LEDs gemeinsam blinken lassen
        for _ in range(3):
            for led in self.leds.values():
                led.on()
            time.sleep(0.2)
            for led in self.leds.values():
                led.off()
            time.sleep(0.2)

    def start(self):
        """
        Haupt-Loop:
        - wartet auf Start (Wave + Button)
        - setzt neue Folge
        - Runde für Runde: eine neue Farbe anhängen, Folge abspielen, Eingabe prüfen
        - bei Fehler: Game Over Signal, dann zurück zur Start-Warteschleife
        """
        while True:
            self.wait_for_start_with_wave()

            # neue Session beginnt -> Folge zurücksetzen
            self.sequence = []
            game_active = True

            while game_active:
                # nächste Farbe zur Folge hinzufügen
                self.sequence.append(random.choice(self.colors))

                # Simon spielt die Folge ab
                self.play_sequence()

                # Spieler versucht nachzumachen
                if not self.get_player_input():
                    self.game_over_signal()
                    game_active = False
                else:
                    # kleine Pause vor der nächsten Runde
                    time.sleep(0.8)


if __name__ == "__main__":
    # Startet das Spiel direkt, wenn das Skript ausgeführt wird
    game = SimonSaysGame()
    game.start()
