from threading import Lock
from typing import Dict
from things_game.logic import ThingsGame
from things_game.utils import generate_id


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