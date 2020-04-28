import os
import logging

import eventlet
eventlet.monkey_patch()

import flask
from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room, send, emit

from things_game.logic import GameState, ThingsGame
from things_game.manager import GameManager
from things_game.utils import unpack
from things_game.errors import GameStateError, PlayerError, InputError
from things_game.background_scheduler import BackgroundTaskScheduler
from things_game.topics import TopicsList


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
topics = TopicsList()


def _prune_task():
    logger.info("Pruning games...")
    games_removed = manager.prune()
    for game_id in games_removed:
        socketio.close_room(game_id)


# TODO: Re-enable pruning
background_scheduler.run_every(15*60, _prune_task)


class GameCommand(unpack):
    def __init__(self, *args, **kwargs):
        super(GameCommand, self).__init__(*args, **kwargs, game_id="")

    def __call__(self, func):
        def f(game_id, *args, **kwargs):
            game = manager.get_game(game_id)
            if not game:
                send_error("Unable to find game")
                return
            return func(game, *args, **kwargs)

        return super(GameCommand, self).__call__(f)


def send_error(message):
    logger.error(message, exc_info=True)
    emit("error", dict(error=message))


def send_update(event, game, player=None, context_aware=True):
    data = {"game": game.to_dict()}
    if player:
        data["player"] = player.to_dict()
    emit_func = emit if context_aware else socketio.emit
    emit_func(event, data, broadcast=True, room=game.info.game_id)


@socketio.on("request_update")
@unpack(game_id="", player_id="", session_key="")
def request_update(game_id, player_id, session_key):
    response = {"game": None}
    game = manager.get_game(game_id)
    if game:
        try:
            game.validate_player(player_id, session_key, can_be_observer=True)
            manager.update_player_sid(game_id, player_id, flask.request.sid)
            try:
                join_room(game.id)
            except Exception as e:
                logger.exception(e)
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
@unpack(name="", password="", salt="", player_name="Unknown", color=DEFAULT_PLAYER_COLOR, observer=False)
def create_game(name, password, salt, player_name, color, observer):
    game = manager.create_game(name, password, salt)
    player = game.add_player(player_name, observer, color)
    manager.update_player_sid(game.id, player.id, flask.request.sid)

    join_room(game.info.game_id)
    send_update("player_joined", game, player)
    emit("player_id", {"player_id": player.id, "session_key": player.session_key})


@socketio.on("join_game")
@GameCommand(password="", player_name="Unknown", color=DEFAULT_PLAYER_COLOR, observer=False)
def join_game(game: ThingsGame, password, player_name, color, observer):
    if game.password != password:
        send_error("Incorrect password")
        return
    player = game.add_player(player_name, observer, color)
    manager.update_player_sid(game.id, player.id, flask.request.sid)

    join_room(game.id)
    send_update("player_joined", game, player)
    emit("player_id", {"player_id": player.id, "session_key": player.session_key})


@socketio.on("leave_game")
@GameCommand(player_id="", session_key="")
def leave_game(game: ThingsGame, player_id, session_key):
    try:
        initial_state = game.info.state
        leave_room(game.id)
        manager.remove_player_sid(game.id, player_id)
        player = game.remove_player(player_id, session_key)
        new_state = game.info.state
        send_update("player_left", game, player)
    except PlayerError:
        return
    if initial_state == new_state:
        return
    if new_state == GameState.round_complete:
        game.start_round()
        send_update("round_started", game)


@socketio.on("remove_player")
@GameCommand(player_id="", session_key="", player_id_to_remove="")
def remove_player(game: ThingsGame, player_id, session_key, player_id_to_remove):
    try:
        initial_state = game.info.state
        player = game.force_remove_player(player_id, session_key, player_id_to_remove)
        new_state = game.info.state
        send_update("player_removed", game, player)

        player_sid = manager.remove_player_sid(game.id, player_id_to_remove)
        if player_sid:
            leave_room(game.id, player_sid)
    except PlayerError as e:
        send_error(str(e))
        return
    if initial_state != new_state and new_state == GameState.round_complete:
        game.start_round()
        send_update("round_started", game)


@socketio.on("change_color")
@GameCommand(player_id="", session_key="", color="")
def change_color(game: ThingsGame, player_id, session_key, color):
    try:
        if not color:
            raise InputError("Failed to set color")
        player = game.validate_player(player_id, session_key)
        player.color = color
    except (GameStateError, PlayerError, InputError) as e:
        send_error(str(e))


@socketio.on("start_game")
@GameCommand(player_id="", session_key="")
def start_game(game: ThingsGame, player_id, session_key):
    try:
        game.start_game(player_id, session_key)
        send_update("game_started", game)
    except (GameStateError, PlayerError, InputError) as e:
        send_error(str(e))


@socketio.on("reset_points")
@GameCommand(player_id="", session_key="")
def reset_points(game: ThingsGame, player_id, session_key):
    try:
        game.reset_points(player_id, session_key)
        send_update("points_reset", game)
    except (GameStateError, PlayerError, InputError) as e:
        send_error(str(e))


@socketio.on("get_random_topic")
def get_random_topic():
    topic = topics.get_random_topic()
    emit("random_topic", {"text": topic})


@socketio.on("set_topic")
@GameCommand(player_id="", session_key="", topic="")
def set_topic(game: ThingsGame, player_id, session_key, topic):
    if not topic:
        send_error("Topic was not set")
        return
    try:
        game.set_topic(player_id, session_key, topic)
        send_update("topic_set", game)
    except (GameStateError, PlayerError, InputError) as e:
        send_error(str(e))


@socketio.on("skip_topic_writer")
@GameCommand(player_id="", session_key="")
def skip_topic_writer(game: ThingsGame, player_id, session_key):
    try:
        game.skip_topic_writer(player_id, session_key)
        send_update("topic_writer_skipped", game)
    except (GameStateError, PlayerError, InputError) as e:
        send_error(str(e))


@socketio.on("submit_answer")
@GameCommand(player_id="", session_key="", answer="")
def submit_answer(game: ThingsGame, player_id, session_key, answer):
    if not answer:
        send_error("Answer was not provided")
        return
    try:
        game.submit_answer(player_id, session_key, answer)
        send_update("answer_submitted", game)
    except (GameStateError, PlayerError, InputError) as e:
        send_error(str(e))


@socketio.on("skip_answer")
@GameCommand(player_id="", session_key="")
def skip_answer(game: ThingsGame, player_id, session_key):
    try:
        pass
    except (GameStateError, PlayerError, InputError) as e:
        send_error(str(e))



@socketio.on("submit_match")
@GameCommand(player_id="", session_key="", guessed_player_id="", answer_id="")
def submit_match(game: ThingsGame, player_id, session_key, guessed_player_id, answer_id):
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
        background_scheduler.run_in(6, round_started)

    def finalize():
        result = game.finalize_match(player, guessed_answer, guessed_player_answer)
        match_result_data = {"game": game.info.to_dict(), "result": result}
        socketio.emit("match_result", match_result_data,
                      room=game.info.game_id)
        if game.info.state == GameState.round_complete:
            background_scheduler.run_in(2, round_complete)

    background_scheduler.run_in(3, finalize)
