import threading
from flask import Flask
from flask_socketio import SocketIO

# Global verfügbar machen
socketio = SocketIO()
game_instance = None

def create_app():
    global game_instance
    app = Flask(__name__)
    app.config.from_object('app.config')
    app.config['SECRET_KEY'] = 'simon_secret_key'

    # Extensions initialisieren
    import app.db as my_db
    my_db.init_app(app)
    
    # Wir erzwingen 'threading' mode, da wir manuell Threads starten und eventlet Konflikte verursacht
    socketio.init_app(app, cors_allowed_origins="*", async_mode="threading")

    # Blueprints registrieren
    from app.routes.main import main_bp
    from app.routes.remote import remote_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(remote_bp)

    # Datenbankmodelle laden und Tabellen erstellen
    with app.app_context():
        my_db.init_db()

    # WICHTIG: Import hier, um Zirkelbezüge zu vermeiden
    from app.gpio_logic import SimonSaysGame

    def game_socket_callback(event, data):
        try:
            with app.app_context():
                socketio.emit(event, data, namespace='/remote')
                socketio.emit(event, data) # Default namespace
        except Exception as e:
            print(f"ERROR inside game_socket_callback: {e}")

    try:
        # Instanz erstellen
        game_instance = SimonSaysGame(socket_callback=game_socket_callback)

        # Hardware-Thread starten
        game_thread = threading.Thread(target=game_instance.start_game_loop, daemon=True)
        game_thread.start()
    except Exception as exc:
        game_instance = None
        app.logger.exception("SimonSays Hardware konnte nicht initialisiert werden: %s", exc)

    return app