from typing import List, Dict
import os
import logging
from threading import Lock
from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room, send, emit

from things_game.logic import ThingsGame
from things_game.utils import generate_id
from things_game.errors import GameStateError, PlayerError, InputError


logging.basicConfig(format="[%(asctime)s] [%(threadName)s] [%(name)s.%(funcName)s:%(lineno)s] [%(levelname)s]: %(message)s",
                    level="DEBUG")
logger = logging.getLogger(__name__)


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = os.getenv("THINGS_GAME_SECRET_KEY", "")


class GameManager(object):
    def __init__(self):
        self.lock = Lock()
        self.games: Dict[str, ThingsGame] = {}

    def get_games(self):
        with self.lock:
            return self.games.values()[:]

    def create_game(self, name, password_hash, password_salt):
        with self.lock:
            game_id = generate_id()
            while game_id in self.games:
                game_id = generate_id()

            if not name:
                name = game_id
            game = ThingsGame(name, password_hash, password_salt, game_id)
            self.games[game_id] = game
            return game

    def get_game(self, game_id):
        with self.lock:
            return self.games.get(game_id, None)


manager = GameManager()


def send_error(message):
    emit("error", dict(error=message))


def send_update(event, game, player=None):
    data = {"game": game.info.to_dict()}
    if player:
        data["player"] = player.to_dict()
    emit(event, data, broadcast=True, room=game.info.game_id, include_self=True)


@socketio.on("get_games")
def get_games():
    games = []
    for game in manager.get_games():
        games.append({
            "id": game.info.id,
            "name": game.info.name,
            "password_protected": game.password != "",
            "password_salt": game.salt,
        })
    emit("games", {"games": games})


@socketio.on("create_game")
def create_game(data):
    gameroom_name = data.get("name", "")
    password_hash = data.get("password", "")
    password_salt = data.get("salt", "")
    player_name = data.get("player_name", "Unknown")
    observer = data.get("observer", False)

    game = manager.create_game(gameroom_name, password_hash, password_salt)
    player = game.add_player(player_name, observer)

    join_room(game.info.game_id)
    send_update("player_joined", game, player)
    emit("player_id", {"player_id": player.id, "session_key": player.session_key})


@socketio.on("join_game")
def join_game(data):
    game_id = data.get("game_id", "")
    password = data.get("password", "")
    player_name = data.get("player_name")
    observer = data.get("observer", False)

    game = manager.get_game(game_id)
    if not game:
        send_error("Unable to find game")
        return
    if game.password != password:
        send_error("Incorrect password")
        return
    player = game.add_player(player_name, observer)

    join_room(game_id)
    send_update("player_joined", game, player)
    emit("player_id", {"player_id": player.id, "session_key": player.session_key})


@socketio.on("leave_game")
def leave_game(data):
    game_id = data.get("id", "")
    player_id = data.get("player_id")

    game = manager.get_game(game_id)
    if not game:
        send_error("Unable to find game")
        return

    leave_room(game_id)
    player = game.remove_player(player_id)
    if player:
        send_update("player_left", game, player)


@socketio.on("start_game")
def start_game(data):
    game_id = data.get("id", "")
    player_id = data.get("player_id")

    game = manager.get_game(game_id)
    if not game:
        send_error("Unable to find game")
        return

    try:
        game.start_game(player_id)
        send_update("game_started", game)
    except (GameStateError, PlayerError, InputError) as e:
        send_error(str(e))


@app.route("/")
def index():
    return dict(hello='world')
