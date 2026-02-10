import threading
from flask import Flask
from flask_socketio import SocketIO

# Global verfügbar machen
socketio = SocketIO()
game_instance = None

def create_app():
    global game_instance
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'simon_secret_key'

    # SocketIO starten
    socketio.init_app(app, cors_allowed_origins="*")

    # Blueprints registrieren
    from app.routes.main import main_bp
    from app.routes.remote import remote_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(remote_bp)

    # --- HIER IST DIE WICHTIGE VERBINDUNG ---
    from app.gpio_logic import SimonSaysGame

    # Diese Funktion ist der Bote, der die Nachricht vom Spiel an die Webseite trägt
    def game_socket_callback(event, data):
        # WICHTIG: namespace='/remote' muss gesetzt sein!
        socketio.emit(event, data, namespace='/remote')

    # Spiel erstellen und den Boten (Callback) mitgeben
    game_instance = SimonSaysGame(socket_callback=game_socket_callback)

    # Hardware-Thread starten
    game_thread = threading.Thread(target=game_instance.start_game_loop, daemon=True)
    game_thread.start()

    return app