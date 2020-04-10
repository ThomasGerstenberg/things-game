from typing import List, Dict
import os
import logging
import time
from threading import Lock, Thread

import eventlet
eventlet.monkey_patch()

import flask
from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room, send, emit

from things_game.logic import GameState
from things_game.manager import GameManager
from things_game.utils import generate_id
from things_game.errors import GameStateError, PlayerError, InputError
from things_game.background_scheduler import BackgroundTaskScheduler


logging.basicConfig(format="[%(asctime)s] [%(threadName)s] [%(name)s.%(funcName)s:%(lineno)s] [%(levelname)s]: %(message)s",
                    level="DEBUG")
logger = logging.getLogger(__name__)


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = os.getenv("THINGS_GAME_SECRET_KEY", "")

DEFAULT_PLAYER_COLOR = "blue"


manager = GameManager()
background_scheduler = BackgroundTaskScheduler()
background_scheduler.start()


def send_error(message):
    emit("error", dict(error=message))


def send_update(event, game, player=None, context_aware=True):
    data = {"game": game.info.to_dict()}
    if player:
        data["player"] = player.to_dict()
    emit_func = emit if context_aware else socketio.emit
    emit_func(event, data, broadcast=True, room=game.info.game_id)


class unpack(object):
    def __init__(self, *args, **kwargs):
        self.required = args
        self.optional = kwargs

    def __call__(self, func):
        def f(data):
            kwargs = {}
            for arg in self.required:
                kwargs[arg] = data[arg]
            for name, default in self.optional.items():
                kwargs[name] = data.get(name, default)
            func(**kwargs)
        return f


@socketio.on("request_update")
@unpack(game_id="", player_id="", session_key="")
def request_update(game_id, player_id, session_key):
    response = {"game": None}
    game = manager.get_game(game_id)
    if game:
        try:
            game.validate_player(player_id, session_key, can_be_observer=True)
            response["game"] = game.info.to_dict()
        except PlayerError as e:
            send_error(str(e))
    emit("game_update", response)


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
@unpack(name="", password="", salt="", player_name="Unknown",
        color=DEFAULT_PLAYER_COLOR, observer=False)
def create_game(name, password, salt, player_name, color, observer):
    game = manager.create_game(name, password, salt)
    player = game.add_player(player_name, observer, color)

    join_room(game.info.game_id)
    send_update("player_joined", game, player)
    emit("player_id", {"player_id": player.id, "session_key": player.session_key})


@socketio.on("join_game")
@unpack(game_id="", password="", player_name="Unknown",
        color=DEFAULT_PLAYER_COLOR, observer=False)
def join_game(game_id, password, player_name, color, observer):
    game = manager.get_game(game_id)
    if not game:
        send_error("Unable to find game")
        return
    if game.password != password:
        send_error("Incorrect password")
        return
    player = game.add_player(player_name, observer, color)

    join_room(game_id)
    send_update("player_joined", game, player)
    emit("player_id", {"player_id": player.id, "session_key": player.session_key})


@socketio.on("leave_game")
@unpack(game_id="", player_id="", session_key="")
def leave_game(game_id, player_id, session_key):
    game = manager.get_game(game_id)
    if not game:
        send_error("Unable to find game")
        return

    leave_room(game_id)
    player = game.remove_player(player_id, session_key)
    if player:
        send_update("player_left", game, player)


@socketio.on("start_game")
@unpack(game_id="", player_id="", session_key="")
def start_game(game_id, player_id, session_key):
    game = manager.get_game(game_id)
    if not game:
        send_error("Unable to find game")
        return

    try:
        game.start_game(player_id, session_key)
        send_update("game_started", game)
    except (GameStateError, PlayerError, InputError) as e:
        send_error(str(e))


@socketio.on("set_topic")
@unpack(game_id="", player_id="", session_key="", topic="")
def set_topic(game_id, player_id, session_key, topic):
    if not topic:
        send_error("Topic was not set")
        return

    game = manager.get_game(game_id)
    if not game:
        send_error("Unable to find game")
        return

    try:
        game.set_topic(player_id, session_key, topic)
        send_update("topic_set", game)
    except (GameStateError, PlayerError, InputError) as e:
        send_error(str(e))


@socketio.on("submit_answer")
@unpack(game_id="", player_id="", session_key="", answer="")
def submit_answer(game_id, player_id, session_key, answer):
    if not answer:
        send_error("Answer was not provided")
        return

    game = manager.get_game(game_id)
    if not game:
        send_error("Unable to find game")
        return

    try:
        game.submit_answer(player_id, session_key, answer)
        send_update("answer_submitted", game)
    except (GameStateError, PlayerError, InputError) as e:
        send_error(str(e))


@socketio.on("submit_match")
@unpack(game_id="", player_id="", session_key="", guessed_player_id="", answer_id="")
def submit_match(game_id, player_id, session_key, guessed_player_id, answer_id):
    game = manager.get_game(game_id)
    if not game:
        send_error("Unable to find game")
        return

    try:
        player, guessed_answer, guessed_player_answer = game.validate_match(player_id, session_key,
                                                                            answer_id, guessed_player_id)
        data = {"player": player.to_dict(),
                "guessed_answer": guessed_answer.to_dict(),
                "guessed_player": guessed_player_answer.player.to_dict()}
        emit("match_submitted", data, broadcast=True, room=game.info.game_id, include_self=True)
    except (GameStateError, PlayerError, InputError) as e:
        send_error(str(e))
        return

    def round_started():
        game.start_round()
        send_update("round_started", game, context_aware=False)

    def round_complete():
        round_complete_data = {"winner": player.to_dict()}
        socketio.emit("round_complete", round_complete_data,
                      broadcast=True, room=game.info.game_id)
        background_scheduler.run_in(8, round_started)

    def finalize():
        result = game.finalize_match(player, guessed_answer, guessed_player_answer)
        match_result_data = {"game": game.info.to_dict(), "result": result}
        socketio.emit("match_result", match_result_data,
                      room=game.info.game_id)
        if game.info.state == GameState.round_complete:
            background_scheduler.run_in(2, round_complete)

    background_scheduler.run_in(3, finalize)


@app.route("/")
def index():
    return dict(hello='world')
