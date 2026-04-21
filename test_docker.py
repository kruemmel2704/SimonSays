import sys

# Patch tkinter to simulate Docker missing tkinter
class DummyImporter:
    def find_spec(self, fullname, path, target=None):
        if fullname == 'tkinter':
            raise ImportError("No module named 'tkinter'")
        return None

sys.meta_path.insert(0, DummyImporter())


# Also we simulate the issue of `game_instance`
from app.gpio_logic import SimonSaysGame
print("Starting instantiation...")
try:
    game = SimonSaysGame(socket_callback=lambda event, data: None)
    print("Game created successfully.")
except Exception as e:
    import traceback
    traceback.print_exc()

