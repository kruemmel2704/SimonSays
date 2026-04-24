from flask import Blueprint
from flask_socketio import emit
from app import socketio

remote_bp = Blueprint('remote', __name__)

def game_socket_callback(event, data):
    # Ohne namespace='/remote' kommt in der remote.html nichts an!
    socketio.emit(event, data, namespace='/remote')

@socketio.on('connect', namespace='/remote')
def handle_connect():
    print("Remote-Client verbunden!")
    emit('game_status', {'msg': 'Remote verbunden'})

    import app
    if app.game_instance:
        emit('led_snapshot', {'states': app.game_instance.get_led_snapshot()})
        emit('difficulty_changed', {'level': app.game_instance.current_difficulty})

@socketio.on('remote_input', namespace='/remote')
def handle_remote_input(data):
    color = data.get('color')
    print(f"Web-Input empfangen: {color}")
    
    import app
    if app.game_instance:
        # Wir schicken NUR den Input an die Logik.
        # Die Logik ruft dann flash_led() auf, was das 'on' UND 'off' Signal 
        # an alle Browser sendet.
        app.game_instance.process_remote_input(color)
    else:
        print("Fehler: game_instance ist nicht initialisiert!")

@socketio.on('change_difficulty', namespace='/remote')
def handle_difficulty(data):
    level = data.get('level')
    from app.config import DIFFICULTY_SETTINGS
    import app

    if level in DIFFICULTY_SETTINGS and app.game_instance:
        app.game_instance.set_difficulty(level)

@socketio.on('submit_highscore', namespace='/remote')
def handle_submit_highscore(data):
    name = data.get('name')
    print(f"Highscore-Name empfangen: {name}")
    import app
    if app.game_instance:
        # Reicht den Namen an die Spiellogik weiter
        app.game_instance.on_name_submitted(name)

@socketio.on('start_game', namespace='/remote')
def handle_start_game():
    print("Start-Signal vom Web empfangen")
    import app
    if app.game_instance:
        app.game_instance.process_remote_input("START_SIGNAL")

@socketio.on('request_snapshot', namespace='/remote')
def handle_request_snapshot():
    """Erlaubt dem Frontend ein aktives Nachziehen des Live-Zustands."""
    import app
    if app.game_instance:
        emit('led_snapshot', {'states': app.game_instance.get_led_snapshot()})
        emit('difficulty_changed', {'level': app.game_instance.current_difficulty})
