import threading
import sys
from app import create_app, socketio
from app.config import IS_RASPI

# Erstellen der App-Instanz über die Factory-Funktion
app = create_app()

def start_server():
    # use_reloader=False ist wichtig, wenn wir manuell Threads starten
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True, use_reloader=False)

if __name__ == "__main__":
    try:
        print("  ██████  ██▓ ███▄ ▄███▓ ▒█████   ███▄    █      ██████  ▄▄▄     ▓██   ██▓  ██████ ")
        print("▒██    ▒ ▓██▒▓██▒▀█▀ ██▒▒██▒  ██▒ ██ ▀█   █    ▒██    ▒ ▒████▄    ▒██  ██▒▒██    ▒ ")
        print("░ ▓██▄   ▒██▒▓██    ▓██░▒██░  ██▒▓██  ▀█ ██▒   ░ ▓██▄   ▒██  ▀█▄   ▒██ ██░░ ▓██▄   ")
        print("  ▒   ██▒░██░▒██    ▒██ ▒██   ██░▓██▒  ▐▌██▒     ▒   ██▒░██▄▄▄▄██  ░ ▐██▓░  ▒   ██▒")
        print("▒██████▒▒░██░▒██▒   ░██▒░ ████▓▒░▒██░   ▓██░   ▒██████▒▒ ▓█   ▓██▒ ░ ██▒▓░▒██████▒▒")
        print("▒ ▒▓▒ ▒ ░░▓  ░ ▒░   ░  ░░ ▒░▒░▒░ ░ ▒░   ▒ ▒    ▒ ▒▓▒ ▒ ░ ▒▒   ▓▒█░  ██▒▒▒ ▒ ▒▓▒ ▒ ░")
        print("░ ░▒  ░ ░ ▒ ░░  ░      ░  ░ ▒ ▒░ ░ ░░   ░ ▒░   ░ ░▒  ░ ░  ▒   ▒▒ ░▓██ ░▒░ ░ ░▒  ░ ░")
        print("░  ░  ░   ▒ ░░      ░   ░ ░ ░ ▒     ░   ░ ░    ░  ░  ░    ░   ▒   ▒ ▒ ░░  ░  ░  ░  ")
        print("      ░   ░         ░       ░ ░           ░          ░        ░  ░░ ░           ░  ")
        print("                                                                  ░ ░                   ")
    except UnicodeEncodeError:
        print("--- Simon Says ---")

    print("--- Simon Says Web-Server wird gestartet ---")
    
    # Server in einem Daemon-Thread starten, damit wir den Main-Thread für GUI nutzen können
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    if not IS_RASPI:
        try:
            print("Starte GUI-Emulator...")
            from mock_gpio_gui import _get_emulator
            _get_emulator().run()
        except ImportError:
            print("WARNUNG: mock_gpio_gui konnte nicht geladen werden. Server läuft Headless.")
            server_thread.join()
        except KeyboardInterrupt:
            print("Beende...")
    else:
        # Auf dem Pi läuft nur der Server
        try:
            server_thread.join()
        except KeyboardInterrupt:
            print("Beende...")