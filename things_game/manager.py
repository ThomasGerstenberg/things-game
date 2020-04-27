from threading import Lock
from typing import Dict
import logging
import time
from things_game.logic import ThingsGame
from things_game.utils import generate_id, generate_game_id


logger = logging.getLogger(__name__)


def _sid_key(game_id, player_id):
    return f"{game_id}.{player_id}"


class GameManager(object):
    def __init__(self):
        self.lock = Lock()
        self.games: Dict[str, ThingsGame] = {}
        self.player_sids = {}

    def update_player_sid(self, game_id, player_id, sid):
        with self.lock:
            self.player_sids[_sid_key(game_id, player_id)] = sid

    def get_player_sid(self, game_id, player_id):
        with self.lock:
            return self.player_sids.get(_sid_key(game_id, player_id), "")

    def remove_player_sid(self, game_id, player_id):
        with self.lock:
            sid = ""
            key = _sid_key(game_id, player_id)
            if key in self.player_sids:
                sid = self.player_sids[key]
                del self.player_sids[key]
            return sid

    def prune(self, stale_time_seconds=15*60):
        games_to_remove = {}
        now = time.time()
        with self.lock:
            for game_id, game in self.games.items():
                t_since_last_update = now - game.last_update_time
                if t_since_last_update > stale_time_seconds or not game.info.players:
                    games_to_remove[game_id] = []
                    logger.info(f"Pruning game {game_id}, {int(t_since_last_update)} seconds since last update "
                                f"(created {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(game.create_time))}). "
                                f"Players: {len(game.info.players)}")

            for game_id in games_to_remove:
                del self.games[game_id]

            game_players_to_remove = []
            for game_player_id, sid in self.player_sids.items():
                game_id, player_id = game_player_id.split(".")
                if game_id in games_to_remove:
                    games_to_remove[game_id].append(player_id)
                    game_players_to_remove.append(game_player_id)

            for p in game_players_to_remove:
                del self.player_sids[p]
            return games_to_remove

    def get_games(self):
        with self.lock:
            return self.games.values()[:]

    def create_game(self, name, password_hash, password_salt):
        with self.lock:
            game_id = generate_game_id()
            i = 0
            while game_id in self.games:
                if i < 100:
                    game_id = generate_game_id()
                else:
                    game_id = generate_id()

            if not name:
                name = game_id
            game = ThingsGame(name, password_hash, password_salt, game_id)
            self.games[game_id] = game
            return game

    def get_game(self, game_id):
        with self.lock:
            return self.games.get(game_id, None)