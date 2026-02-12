from flask import Blueprint, current_app
from flask_socketio import emit
from app import socketio

remote_bp = Blueprint('remote', __name__)

def game_socket_callback(event, data):
    # Ohne namespace='/remote' kommt in der remote.html nichts an!
    socketio.emit(event, data, namespace='/remote')

@socketio.on('connect', namespace='/remote')
def handle_connect():
    print("Client verbunden mit /remote")
    emit('status', {'msg': 'Verbunden mit SimonSays Remote'})

    import app
    if app.game_instance:
        emit('led_snapshot', {'states': app.game_instance.get_led_snapshot()})

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
        settings = DIFFICULTY_SETTINGS[level]
        app.game_instance.flash_delay = settings['flash']
        app.game_instance.sequence_pause = settings['pause']
        print(f"Schwierigkeit auf {level} gesetzt")
        emit('difficulty_changed', {'level': level}, broadcast=True, namespace='/remote')