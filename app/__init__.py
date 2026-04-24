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
    
    # In Container-Umgebungen ist eventlet oder gevent meist stabiler
    # Hier nutzen wir eventlet (passend zum monkey_patch in run.py)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet')

    # Blueprints registrieren
    from app.routes.main import main_bp
    from app.routes.remote import remote_bp
    from app.routes.admin import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(remote_bp)
    app.register_blueprint(admin_bp)

    # Datenbankmodelle laden und Tabellen erstellen
    with app.app_context():
        my_db.init_db()

    # WICHTIG: Import hier, um Zirkelbezüge zu vermeiden
    from app.gpio_logic import SimonSaysGame

    def game_socket_callback(event, data):
        # Print für Docker-Logs zur Diagnose
        # print(f"DEBUG SocketIO: Sende Event '{event}' an Clients...")
        try:
            # Wir emittieren an den Namespace /remote (Dashboard)
            socketio.emit(event, data, namespace='/remote')
            # Fallback für andere Subscriber
            socketio.emit(event, data)
        except Exception as e:
            print(f"ERROR beim Senden von SocketIO Event: {e}")

    try:
        # Instanz erstellen
        game_instance = SimonSaysGame(socket_callback=game_socket_callback)

        # Hardware-Thread starten
        game_thread = threading.Thread(target=game_instance.start_game_loop, daemon=True)
        game_thread.start()
        print("Hardware-Thread für SimonSays wurde gestartet.")
    except Exception as exc:
        game_instance = None
        app.logger.exception("SimonSays Hardware konnte nicht initialisiert werden: %s", exc)

    return app