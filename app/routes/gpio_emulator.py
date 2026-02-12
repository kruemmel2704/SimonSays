import tkinter as tk
from threading import Thread

class GPIOEmulator:
    def __init__(self, setup):
        self.root = tk.Tk()
        self.root.title("Simon Says GPIO Emulator")
        self.root.geometry("300x400")
        self.root.attributes("-topmost", True) # Immer im Vordergrund
        
        self.led_widgets = {}
        self.button_states = {color: False for color in setup}

        for color, pins in setup.items():
            frame = tk.Frame(self.root, pady=5)
            frame.pack()
            
            # LED Anzeige (Kreis/Label)
            led = tk.Label(frame, text=f"LED {color.upper()}", bg="grey", width=15, height=2)
            led.pack(side=tk.LEFT)
            self.led_widgets[color] = led
            
            # Button Simulation
            btn = tk.Button(frame, text="DRÜCKEN", command=lambda c=color: self._press(c))
            btn.pack(side=tk.RIGHT)

        # Buzzer Anzeige
        self.buzzer_label = tk.Label(self.root, text="Buzzer: SILENT", bg="white", pady=10)
        self.buzzer_label.pack(fill=tk.X)

    def _press(self, color):
        self.button_states[color] = True
        # Nach 200ms automatisch wieder loslassen (simuliert Tastendruck)
        self.root.after(200, lambda: self._reset_press(color))

    def _reset_press(self, color):
        self.button_states[color] = False

    def set_led(self, color, state):
        bg = color if state else "grey"
        self.led_widgets[color].config(bg=bg)

    def set_buzzer(self, state):
        text = "Buzzer: BEEPING!" if state else "Buzzer: SILENT"
        bg = "yellow" if state else "white"
        self.buzzer_label.config(text=text, bg=bg)

    def run(self):
        self.root.mainloop()

# Globale Instanz für den Zugriff
emulator = None

def start_emulator(setup):
    global emulator
    emulator = GPIOEmulator(setup)
    Thread(target=emulator.run, daemon=True).start()