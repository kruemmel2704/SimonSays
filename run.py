from app import create_app, socketio

# Erstellen der App-Instanz über die Factory-Funktion
app = create_app()

if __name__ == "__main__":
    
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
    # Wir nutzen socketio.run anstelle von app.run, 
    # damit die WebSocket-Verbindung (Echtzeit) stabil funktioniert.
    # host='0.0.0.0' macht den Server im lokalen Netzwerk erreichbar.
    print("--- Simon Says Web-Server wird gestartet ---")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)