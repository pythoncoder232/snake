from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit
import eventlet
import random

app = Flask(__name__, static_url_path='')
socketio = SocketIO(app, cors_allowed_origins="*")
players = {}

@app.route('/')
def index():
    return send_from_directory('', 'index.html')

@socketio.on('connect')
def handle_connect():
    player_id = request.sid
    players[player_id] = {'snake': [{'x': random.randint(0, 79), 'y': random.randint(0, 59)}], 'direction': 'right'}
    emit('init', {'playerId': player_id, 'players': players}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    player_id = request.sid
    if player_id in players:
        del players[player_id]
    emit('state', {'players': players}, broadcast=True)

@socketio.on('keydown')
def handle_keydown(data):
    player_id = data['playerId']
    key = data['key']
    if player_id in players:
        if key == 'ArrowUp' and players[player_id]['direction'] != 'down':
            players[player_id]['direction'] = 'up'
        elif key == 'ArrowDown' and players[player_id]['direction'] != 'up':
            players[player_id]['direction'] = 'down'
        elif key == 'ArrowLeft' and players[player_id]['direction'] != 'right':
            players[player_id]['direction'] = 'left'
        elif key == 'ArrowRight' and players[player_id]['direction'] != 'left':
            players[player_id]['direction'] = 'right'
    emit('state', {'players': players}, broadcast=True)

def move_snake():
    for player_id in players:
        snake = players[player_id]['snake']
        direction = players[player_id]['direction']
        head = snake[0].copy()

        if direction == 'up':
            head['y'] -= 1
        elif direction == 'down':
            head['y'] += 1
        elif direction == 'left':
            head['x'] -= 1
        elif direction == 'right':
            head['x'] += 1

        snake.insert(0, head)
        snake.pop()

    socketio.emit('state', {'players': players})

if __name__ == '__main__':
    eventlet.spawn(move_snake)
    socketio.run(app, host='0.0.0.0', port=5000)