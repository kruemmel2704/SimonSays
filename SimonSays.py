# SimonSay.py
import time
import random
from gpiozero import LED, Button
from config import HARDWARE_SETUP, FLASH_DELAY, SEQUENCE_PAUSE

class SimonSaysGame:
    def __init__(self):
        self.sequence = []
        self.leds = {}
        self.buttons = {}
        self.colors = list(HARDWARE_SETUP.keys())

        # Hardware Initialisierung
        for color, pins in HARDWARE_SETUP.items():
            self.leds[color] = LED(pins["led"])
            self.buttons[color] = Button(pins["btn"])

    def wait_for_start_with_wave(self):
        """Lässt die LEDs dauerhaft pulsieren, bis ein Knopf gedrückt wird."""
        print("Warte auf Spielstart... (Welle läuft)")
        
        # Wir kombinieren die Farben für ein Hin-und-Her (z.B. Rot-Gelb-Grün-Blau-Grün-Gelb)
        # Wir lassen die letzte und erste Farbe weg, damit sie beim Loopen nicht doppelt leuchten
        wave_pattern = self.colors + self.colors[-2:0:-1]
        
        button_pressed = False
        while not button_pressed:
            for color in wave_pattern:
                self.leds[color].on()
                
                # Während die LED leuchtet, prüfen wir kurz, ob ein Knopf gedrückt wurde
                start_time = time.time()
                while time.time() - start_time < 0.1: # 100ms Leuchtdauer
                    for btn_color, btn in self.buttons.items():
                        if btn.is_pressed:
                            button_pressed = True
                            # Alle LEDs sofort ausmachen
                            for l in self.leds.values(): l.off()
                            print(f"Spiel gestartet durch {btn_color}!")
                            time.sleep(0.5) # Kurzer Delay damit der Druck nicht als Spieleingabe zählt
                            return 
                    time.sleep(0.01)
                
                self.leds[color].off()

    def flash_led(self, color):
        self.leds[color].on()
        time.sleep(FLASH_DELAY)
        self.leds[color].off()
        time.sleep(SEQUENCE_PAUSE)

    def play_sequence(self):
        print("Simon zeigt...")
        for color in self.sequence:
            self.flash_led(color)

    def get_player_input(self):
        print("Du bist dran!")
        for expected_color in self.sequence:
            pressed_color = self.wait_for_any_button()
            if pressed_color == expected_color:
                self.flash_led(pressed_color)
            else:
                return False
        return True

    def wait_for_any_button(self):
        while True:
            for color, btn in self.buttons.items():
                if btn.is_pressed:
                    while btn.is_pressed:
                        time.sleep(0.01)
                    return color
            time.sleep(0.01)

    def game_over_signal(self):
        print("Falsch! Game Over.")
        for _ in range(3):
            for led in self.leds.values(): led.on()
            time.sleep(0.2)
            for led in self.leds.values(): led.off()
            time.sleep(0.2)

    def start(self):
        while True:
            # 1. Warte-Modus mit Welle
            self.wait_for_start_with_wave()
            
            # 2. Spiel-Logik
            self.sequence = []
            game_active = True
            
            while game_active:
                self.sequence.append(random.choice(self.colors))
                self.play_sequence()
                
                if not self.get_player_input():
                    self.game_over_signal()
                    game_active = False # Bricht die innere Schleife ab -> zurück zur Welle
                    time.sleep(1)
                else:
                    print("Richtig! Nächste Runde.")
                    time.sleep(0.8)

if __name__ == "__main__":
    game = SimonSaysGame()
    try:
        game.start()
    except KeyboardInterrupt:
        print("\nSpiel beendet.")