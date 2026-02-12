import threading
from flask import Flask
from flask_socketio import SocketIO
from .database import init_db

# Global verfügbar machen
socketio = SocketIO()
game_instance = None

def create_app():
    global game_instance
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'simon_secret_key'

    # SocketIO initialisieren
    socketio.init_app(app, cors_allowed_origins="*")

    # Blueprints registrieren
    from app.routes.main import main_bp
    from app.routes.remote import remote_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(remote_bp)

    # WICHTIG: Import hier, um Zirkelbezüge zu vermeiden
    from app.gpio_logic import SimonSaysGame

    def game_socket_callback(event, data):
        socketio.emit(event, data, namespace='/remote')

    # Instanz erstellen
    game_instance = SimonSaysGame(socket_callback=game_socket_callback)

    # Hardware-Thread starten
    game_thread = threading.Thread(target=game_instance.start_game_loop, daemon=True)
    game_thread.start()

    with app.app_context():
        try:
            init_db()
        except Exception as e:
            logging.error(f"Datenbank-Initialisierung fehlgeschlagen: {e}")
    
    return app