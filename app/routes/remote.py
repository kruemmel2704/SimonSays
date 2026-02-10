from flask import Blueprint, current_app
from flask_socketio import emit
from app import socketio

remote_bp = Blueprint('remote', __name__)

@socketio.on('connect', namespace='/remote')
def handle_connect():
    print("Client verbunden mit /remote")
    emit('status', {'msg': 'Verbunden mit SimonSays Remote'})

@socketio.on('remote_input', namespace='/remote')
def handle_remote_input(data):
    color = data.get('color')
    print(f"Web-Input empfangen: {color}")
    
    # WICHTIG: Wir holen uns die aktuelle Instanz direkt aus dem app-Modul
    import app 
    if app.game_instance:
        app.game_instance.process_remote_input(color)
        # Feedback an alle senden, damit die LED im Browser leuchtet
        emit('led_state', {'color': color, 'state': 'on'}, broadcast=True, namespace='/remote')
    else:
        print("Kritischer Fehler: game_instance ist None!")