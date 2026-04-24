import threading
from flask import Flask
from flask_socketio import SocketIO

# Global verfügbar machen
# logger=True zeigt uns im Docker-Log genau, was passiert
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading', logger=True, engineio_logger=True)
game_instance = None

def create_app():
    global game_instance
    app = Flask(__name__)
    app.config.from_object('app.config')
    app.config['SECRET_KEY'] = 'simon_secret_key'

    # Extensions initialisieren
    import app.db as my_db
    my_db.init_app(app)
    
    socketio.init_app(app)

    # Blueprints registrieren
    from app.routes.main import main_bp
    from app.routes.remote import remote_bp
    from app.routes.admin import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(remote_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        my_db.init_db()

    from app.gpio_logic import SimonSaysGame

    # --- ZENTRALE SOCKET HANDLER (Damit sie garantiert registriert werden) ---
    
    @socketio.on('connect')
    def handle_connect():
        print("Client verbunden!")
        if game_instance:
            socketio.emit('led_snapshot', game_instance.get_led_snapshot())
            socketio.emit('difficulty_changed', {'level': game_instance.current_difficulty})

    @socketio.on('remote_input')
    def handle_input(data):
        color = data.get('color')
        if game_instance:
            game_instance.process_remote_input(color)

    @socketio.on('start_game')
    def handle_start():
        if game_instance:
            game_instance.process_remote_input("START_SIGNAL")

    @socketio.on('submit_highscore')
    def handle_highscore(data):
        name = data.get('name')
        if game_instance:
            game_instance.on_name_submitted(name)

    @socketio.on('change_difficulty')
    def handle_diff(data):
        level = data.get('level')
        if game_instance:
            game_instance.set_difficulty(level)

    @socketio.on('request_snapshot')
    def handle_snap():
        if game_instance:
            socketio.emit('led_snapshot', game_instance.get_led_snapshot())

    def game_socket_callback(event, data):
        try:
            with app.app_context():
                # Wir emittieren jetzt global (ohne Namespace)
                socketio.emit(event, data)
        except Exception as e:
            print(f"ERROR: {e}")

    try:
        game_instance = SimonSaysGame(socket_callback=game_socket_callback)
        game_thread = threading.Thread(target=game_instance.start_game_loop, daemon=True)
        game_thread.start()
        print("Hardware-Thread gestartet.")
    except Exception as exc:
        print(f"Hardware-Fehler: {exc}")

    return app