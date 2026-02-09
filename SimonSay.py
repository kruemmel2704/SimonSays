import time
import random
from gpiozero import LED, Button, Buzzer
from Config import HARDWARE_SETUP, BUZZER_PIN, FLASH_DELAY, SEQUENCE_PAUSE
from flask import Flask

app = Flask("SimonSaysGame")

@app.route("/")

class SimonSaysGame:
    def __init__(self):
        self.sequence = []
        self.leds = {}
        self.buttons = {}
        self.colors = list(HARDWARE_SETUP.keys())
        self.buzzer = Buzzer(BUZZER_PIN)

        for color, pins in HARDWARE_SETUP.items():
            self.leds[color] = LED(pins["led"])
            self.buttons[color] = Button(pins["btn"])

    def beep(self, times, speed=0.1):
        """Lässt den Buzzer x-mal piepen."""
        for _ in range(times):
            self.buzzer.on()
            time.sleep(speed)
            self.buzzer.off()
            if times > 1:
                time.sleep(speed)

    def wait_for_start_with_wave(self):
        wave_pattern = self.colors + self.colors[-2:0:-1]
        button_pressed = False
        while not button_pressed:
            for color in wave_pattern:
                self.leds[color].on()
                start_time = time.time()
                while time.time() - start_time < 0.1:
                    for btn in self.buttons.values():
                        if btn.is_pressed:
                            button_pressed = True
                            for l in self.leds.values(): l.off()
                            # Bestätigungston beim Start
                            self.beep(1, 0.2)
                            return 
                    time.sleep(0.01)
                self.leds[color].off()

    def flash_led(self, color):
        self.leds[color].on()
        self.buzzer.on() # Kurzer Piep während die LED leuchtet
        time.sleep(FLASH_DELAY)
        self.leds[color].off()
        self.buzzer.off()
        time.sleep(SEQUENCE_PAUSE)

    def play_sequence(self):
        # 1x Piepen: Simon zeigt die Folge
        self.beep(1, 0.2)
        time.sleep(0.5)
        for color in self.sequence:
            self.flash_led(color)

    def get_player_input(self):
        # 2x schnell Piepen: Spieler soll eingeben
        self.beep(2, 0.05)
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
                    while btn.is_pressed: time.sleep(0.01)
                    return color
            time.sleep(0.01)

    def game_over_signal(self):
        print("Game Over!")
        # 3x langsam Piepen: Verloren
        self.beep(3, 0.5)
        for _ in range(3):
            for led in self.leds.values(): led.on()
            time.sleep(0.2)
            for led in self.leds.values(): led.off()
            time.sleep(0.2)

    def start(self):
        while True:
            self.wait_for_start_with_wave()
            self.sequence = []
            game_active = True
            while game_active:
                self.sequence.append(random.choice(self.colors))
                self.play_sequence()
                if not self.get_player_input():
                    self.game_over_signal()
                    game_active = False
                else:
                    time.sleep(0.8)

if __name__ == "__main__":
    game = SimonSaysGame()
    game.start()