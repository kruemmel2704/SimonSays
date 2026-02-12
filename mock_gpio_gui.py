import tkinter as tk
import threading
import time

# Global emulator instance
_emulator = None

def _get_emulator():
    global _emulator
    if _emulator is None:
        _emulator = GPIOEmulator()
        _emulator.start()
    return _emulator

class GPIOEmulator:
    def __init__(self):
        self.root = None
        self.leds = {}
        self.buttons = {}
        self.buzzer = None
        self.running = False

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_gui, daemon=True)
        self.thread.start()
        # Wait for GUI to be ready
        while self.root is None:
            time.sleep(0.1)

    def _run_gui(self):
        self.root = tk.Tk()
        self.root.title("GPIO Emulator")
        self.root.geometry("300x500")
        
        tk.Label(self.root, text="Simon Says Emulator", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.root.mainloop()

    def add_led(self, pin, name=None):
        if self.root:
            self.root.after(0, lambda: self._create_led_widget(pin, name))

    def _create_led_widget(self, pin, name):
        frame = tk.Frame(self.main_frame)
        frame.pack(fill=tk.X, pady=5)
        
        label_text = name if name else f"LED (Pin {pin})"
        lbl = tk.Label(frame, text=label_text, width=15, anchor="w")
        lbl.pack(side=tk.LEFT)
        
        status = tk.Label(frame, text="OFF", bg="gray", width=10, relief="sunken")
        status.pack(side=tk.RIGHT)
        
        self.leds[pin] = status

    def set_led(self, pin, state):
        if pin in self.leds:
            color = "red"  # Default generic color
            # Try to guess color from variable names if possible, but here we just map generic
            # In a real app we might map pin to color.
            # actually, let's make it configurable or just bright
            bg_color = "lime" if state else "gray"
            text = "ON" if state else "OFF"
            
            def update():
                if pin in self.leds:
                    self.leds[pin].config(bg=bg_color, text=text)
            
            if self.root:
                self.root.after(0, update)

    def add_button(self, pin, name=None):
        if self.root:
            self.root.after(0, lambda: self._create_button_widget(pin, name))

    def _create_button_widget(self, pin, name):
        frame = tk.Frame(self.main_frame)
        frame.pack(fill=tk.X, pady=5)
        
        label_text = name if name else f"Button (Pin {pin})"
        lbl = tk.Label(frame, text=label_text, width=15, anchor="w")
        lbl.pack(side=tk.LEFT)
        
        btn = tk.Button(frame, text="PUSH", command=lambda: self._press_button(pin))
        btn.pack(side=tk.RIGHT)
        
        self.buttons[pin] = {"state": False, "widget": btn}

    def _press_button(self, pin):
        if pin in self.buttons:
            self.buttons[pin]["state"] = True
            # Auto release after 200ms
            self.root.after(200, lambda: self._release_button(pin))

    def _release_button(self, pin):
        if pin in self.buttons:
            self.buttons[pin]["state"] = False

    def get_button_state(self, pin):
        if pin in self.buttons:
            return self.buttons[pin]["state"]
        return False

    def add_buzzer(self, pin):
        if self.root:
            self.root.after(0, lambda: self._create_buzzer_widget(pin))

    def _create_buzzer_widget(self, pin):
        frame = tk.Frame(self.main_frame)
        frame.pack(fill=tk.X, pady=10)
        
        self.buzzer = tk.Label(frame, text="BUZZER", bg="white", width=20, height=2, relief="raised")
        self.buzzer.pack()

    def set_buzzer(self, pin, state):
        if self.buzzer:
            bg = "red" if state else "white"
            text = "BEEP!" if state else "BUZZER"
            def update():
                if self.buzzer:
                    self.buzzer.config(bg=bg, text=text)
            if self.root:
                self.root.after(0, update)


# --- Mock Classes mimicking gpiozero ---

class Device:
    pin_factory = None
    @staticmethod
    def ensure_pin_factory():
        pass


class LED:
    def __init__(self, pin):
        self.pin = pin
        self.is_active = False
        _get_emulator().add_led(pin, name=f"LED {pin}")
    
    def on(self):
        self.is_active = True
        _get_emulator().set_led(self.pin, True)
    
    def off(self):
        self.is_active = False
        _get_emulator().set_led(self.pin, False)


class Button:
    def __init__(self, pin):
        self.pin = pin
        _get_emulator().add_button(pin, name=f"Button {pin}")

    @property
    def is_pressed(self):
        return _get_emulator().get_button_state(self.pin)


class Buzzer:
    def __init__(self, pin):
        self.pin = pin
        _get_emulator().add_buzzer(pin)

    def on(self):
        _get_emulator().set_buzzer(self.pin, True)

    def off(self):
        _get_emulator().set_buzzer(self.pin, False)
