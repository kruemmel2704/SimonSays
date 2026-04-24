import eventlet
eventlet.monkey_patch()

import os
import sys
from app import create_app, socketio
from app.config import IS_RASPI

# Erstellen der App-Instanz
app = create_app()

if __name__ == "__main__":
    print("--- Simon Says Web-Server wird gestartet ---")
    
    # Check if we should run GUI (only on Local PC, not on Pi/Docker)
    is_headless = os.environ.get('HEADLESS', '0') == '1' or IS_RASPI
    
    if is_headless:
        # Im Headless-Modus (Pi/Docker) läuft der Server direkt im Main-Thread
        print("Starte Server im Main-Thread (Headless-Modus)...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True, use_reloader=False)
    else:
        # Nur auf dem PC: Server im Hintergrund, damit GUI laufen kann
        import threading
        def start_server():
            socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True, use_reloader=False)
        
        print("Starte Server im Hintergrund (GUI-Modus)...")
        t = threading.Thread(target=start_server, daemon=True)
        t.start()
        
        try:
            from mock_gpio_gui import _get_emulator
            _get_emulator().run()
        except Exception as e:
            print(f"GUI konnte nicht gestartet werden: {e}")
            t.join()