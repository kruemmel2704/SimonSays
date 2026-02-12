import tkinter as tk
import threading
import time
from app.config import HARDWARE_SETUP, DIFFICULTY_BUTTONS

def _get_pin_label(pin, device_type="Device"):
    # Check Hardware Colors
    for color, pins in HARDWARE_SETUP.items():
        if pins['led'] == pin:
            return f"{color.upper()} LED ({pin})"
        if pins['btn'] == pin:
            return f"{color.upper()} Btn ({pin})"
    
    # Check Difficulty Buttons
    for level, btn_pin in DIFFICULTY_BUTTONS.items():
        if btn_pin == pin:
            return f"{level.upper()} ({pin})"
            
    return f"{device_type} {pin}"

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
        self.pending_actions = []

    def start(self):
        # Do not start a thread. We will run the GUI in the main thread explicitly.
        self.running = True
        # Actions will be queued until run() is called

    def run(self):
        """Must be called from the main thread"""
        self.root = tk.Tk()
        self.root.title("GPIO Emulator")
        self.root.geometry("300x500")
        
        tk.Label(self.root, text="Simon Says Emulator", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Process queued actions
        self._process_queues()
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.destroy()

    def _process_queues(self):
        # Execute all pending widget creations
        for action in self.pending_actions:
            action()
        self.pending_actions.clear()

    def add_led(self, pin, name=None):
        if self.root:
            self.root.after(0, lambda: self._create_led_widget(pin, name))
        else:
            self.pending_actions.append(lambda: self._create_led_widget(pin, name))

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
            # ... existing logic ...
            color = "red" 
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
        else:
            self.pending_actions.append(lambda: self._create_button_widget(pin, name))

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
            if self.root:
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
        else:
            self.pending_actions.append(lambda: self._create_buzzer_widget(pin))

    def _create_buzzer_widget(self, pin):
        frame = tk.Frame(self.main_frame)
        frame.pack(fill=tk.X, pady=10)
        
        self.buzzer = tk.Label(frame, text="BUZZER", bg="white", width=20, height=2, relief="raised")
        self.buzzer.pack()

    def set_buzzer(self, pin, state):
        # Queue if not ready? Or just ignore early buzzes? Logic says buzzes come later.
        if self.buzzer:
           # ... existing ...
           pass # implementation below
        # If buzzer widget doesn't exist yet, we can't update it. 
        # Usually set_buzzer is called after init.
        if not self.root: return

        if self.buzzer:
            bg = "red" if state else "white"
            text = "BEEP!" if state else "BUZZER"
            def update():
                if self.buzzer:
                    self.buzzer.config(bg=bg, text=text)
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
        name = _get_pin_label(pin, "LED")
        _get_emulator().add_led(pin, name=name)
    
    def on(self):
        self.is_active = True
        _get_emulator().set_led(self.pin, True)
    
    def off(self):
        self.is_active = False
        _get_emulator().set_led(self.pin, False)


class Button:
    def __init__(self, pin):
        self.pin = pin
        name = _get_pin_label(pin, "Button")
        _get_emulator().add_button(pin, name=name)

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
