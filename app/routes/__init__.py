import threading
from flask import Flask
from flask_socketio import SocketIO

# Diese Objekte müssen global verfügbar sein, damit die Routen darauf zugreifen können
socketio = SocketIO()
game_instance = None

def create_app():
    global game_instance
    app = Flask(SimonSaysGame)
    app.config['SECRET_KEY'] = 'simon_secret_key'

    # 1. Socket.IO initialisieren
    # cors_allowed_origins="*" ist wichtig, falls du über verschiedene IPs zugreifst
    socketio.init_app(app, cors_allowed_origins="*")

    # 2. Blueprints registrieren (deine Routen)
    from app.routes.main import main_bp
    from app.routes.remote import remote_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(remote_bp)

    # 3. GPIO-Logik und Spiel-Instanz vorbereiten
    from app.gpio_logic import SimonSaysGame

    # Wir definieren eine Callback-Funktion, die das Spiel nutzt, 
    # um Hardware-Events an Flask-SocketIO zu "senden".
    def game_socket_callback(event, data):
        socketio.emit(event, data, namespace='/remote')

    # Spiel-Instanz erstellen
    game_instance = SimonSaysGame(socket_callback=game_socket_callback)

    # 4. Den Hardware-Thread starten
    # Das Spiel läuft in einer Endlosschleife, daher muss es in den Hintergrund.
    game_thread = threading.Thread(target=game_instance.start_game_loop, daemon=True)
    game_thread.start()
    print("--- Simon Says Hardware-Thread gestartet ---")

    return app