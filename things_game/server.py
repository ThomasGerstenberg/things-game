from typing import List, Dict
import os
import logging
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit

from things_game.logic import ThingsGame
from things_game.utils import generate_id
from things_game.errors import GameStateError, PlayerError, InputError


logging.basicConfig(format="[%(asctime)s] [%(threadName)s] [%(name)s.%(funcName)s:%(lineno)s] [%(levelname)s]: %(message)s",
                    level="DEBUG")
logger = logging.getLogger(__name__)


app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = os.getenv("THINGS_GAME_SECRET_KEY", "")


GAME_ROOMS: Dict[str, ThingsGame] = {}


def send_error(message):
    emit("error", dict(error=message))


def send_update(event, game, player=None):
    data = {"game": game.info.to_dict()}
    if player:
        data["player"] = player.to_dict()
    emit(event, data, broadcast=True, room=game.info.game_id)


@socketio.on("get_games")
def get_games():
    games = []
    for game in GAME_ROOMS.values():
        games.append({
            "id": game.info.id,
            "name": game.info.name,
            "password_protected": game.password != "",
            "password_salt": game.salt,
        })
    emit("games", {"games": games})


@socketio.on("create_game")
def create_game(data):
    game_id = generate_id()
    while game_id in GAME_ROOMS:
        game_id = generate_id()
    gameroom_name = data.get("name", game_id)
    password_hash = data.get("password", "")
    password_salt = data.get("salt", "")
    player_name = data.get("player_name", "Unknown")
    observer = data.get("observer", False)

    game = ThingsGame(gameroom_name, password_hash, password_salt, game_id)
    player = game.add_player(player_name, observer)
    GAME_ROOMS[game_id] = game

    join_room(game_id)
    send_update("player_joined", game, player)
    emit("player_id", {"player_id": player.id})


@socketio.on("join_game")
def join_game(data):
    game_id = data.get("game_id", "")
    password = data.get("password", "")
    player_name = data.get("player_name")
    observer = data.get("observer", False)
    if game_id not in GAME_ROOMS:
        send_error("Unable to find game")
        return
    game = GAME_ROOMS[game_id]
    if game.password != password:
        send_error("Incorrect password")
        return
    player = game.add_player(player_name, observer)

    join_room(game_id)
    send_update("player_joined", game, player)
    emit("player_id", {"player_id": player.id})


@socketio.on("leave_game")
def leave_game(data):
    game_id = data.get("id", "")
    player_id = data.get("player_id")
    if game_id not in GAME_ROOMS:
        send_error("Unable to find game")
        return
    game = GAME_ROOMS[game_id]
    player = game.remove_player(player_id)
    if player:
        send_update("player_left", game, player)


@socketio.on("start_game")
def start_game(data):
    game_id = data.get("id", "")
    player_id = data.get("player_id")
    if game_id not in GAME_ROOMS:
        send_error("Unable to find game")
        return
    game = GAME_ROOMS[game_id]
    try:
        game.start_game(player_id)
    except (GameStateError, PlayerError, InputError) as e:
        send_error(str(e))
        return
    send_update("game_started", game)


@app.route("/")
def index():
    return dict(hello='world')

