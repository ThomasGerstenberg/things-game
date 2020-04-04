from typing import List, Optional
from enum import Enum
import random
from threading import RLock

from things_game.errors import GameStateError, PlayerError, InputError
from things_game.utils import to_dict, generate_id, generate_key

rand = random.SystemRandom()


class GameState(Enum):
    not_started = "not_started"
    writing_topic = "writing_topic"
    writing_answers = "writing_answers"
    matching = "matching"
    round_complete = "round_complete"
    game_over = "game_over"


class Player(object):
    def __init__(self, name, player_id="", is_observer=False, is_owner=False):
        self.name = name
        self.id = player_id or generate_id()
        self.session_key = generate_key()
        self.is_observer = is_observer
        self.is_owner = is_owner
        self.is_topic_writer = False
        self.is_guessing = False
        self.answer = ""
        self.score = 0

    def to_dict(self):
        return to_dict(self, omit="session_key")


class GameInfo(object):
    def __init__(self, name, game_id, score_limit):
        self.name = name
        self.game_id = game_id
        self.score_limit = score_limit
        self.state = GameState.not_started
        self.players: List[Player] = []
        self.observers: List[Player] = []
        self.topic_writer: Optional[Player] = None
        self.guesser: Optional[Player] = None
        self.current_topic = ""
        self.unguessed_answers = []

    def to_dict(self):
        return to_dict(self)


class ThingsGame(object):
    def __init__(self, name, password_hash="", salt="", game_id="", score_limit=11):
        self.info = GameInfo(name, game_id or generate_id(), score_limit)
        self.password = password_hash
        self.salt = salt
        self.owner: Optional[Player] = None
        self.lock = RLock()
        self.player_answers = {}

    def _generate_player_id(self):
        player_id = generate_id()
        current_ids = [p.id for p in self.info.players + self.info.observers]
        while player_id in current_ids:
            player_id = generate_id()
        return player_id

    def _find_player(self, player_id, player_list: List[Player] = None):
        if player_list is None:
            player_list = self.info.players

        for p in player_list:
            if player_id == p.id:
                return p
        return PlayerError(f"Unable to find player with id {player_id}")

    def _get_next_player(self, player: Player, player_list: List[Player] = None):
        if player_list is None:
            player_list = self.info.players
        index_next = player_list.index(player) + 1
        return player_list[index_next % len(player_list)]

    def _select_next_topic_writer(self):
        if not self.info.topic_writer:
            self.info.topic_writer = rand.choice(self.info.players)
        else:
            # Select the next person
            self.info.topic_writer.is_topic_writer = False
            self.info.topic_writer = self._get_next_player(self.info.topic_writer)

        self.info.topic_writer.is_topic_writer = True

    def _select_next_guesser(self, guessers_remaining=None):
        if not guessers_remaining:
            self.info.guesser = self._get_next_player(self.info.topic_writer)
        else:
            self.info.guesser.is_guessing = False
            self.info.guesser = self._get_next_player(self.info.guesser, guessers_remaining)
            self.info.guesser.is_guessing = True

    def add_player(self, name, is_observer, player_id=""):
        with self.lock:
            if not player_id:
                player_id = self._generate_player_id()

            player = Player(name, player_id, is_observer, not self.info.players)
            if is_observer:
                self.info.observers.append(player)
            else:
                self.info.players.append(player)
            return player

    def remove_player(self, player_id):
        with self.lock:
            try:
                player = self._find_player(player_id)
            except PlayerError:
                try:
                    player = self._find_player(player_id, self.info.observers)
                    self.info.observers.remove(player)
                    return player
                except PlayerError:
                    return None
            if self.info.state == GameState.writing_topic:
                if self.info.topic_writer == player:
                    self._select_next_topic_writer()
            elif self.info.state == GameState.writing_answers:
                if player in self.player_answers:
                    del self.player_answers[player]
            elif self.info.state == GameState.matching:
                guessers_remaining = [p for p in self.info.players if p.is_guessing]
                if player in guessers_remaining:
                    if len(guessers_remaining) <= 2:
                        self.info.state = GameState.round_complete
                    elif player is self.info.guesser:
                        self._select_next_guesser(guessers_remaining)
            self.info.players.remove(player)
            return player

    def start_game(self, player_id):
        with self.lock:
            player = self._find_player(player_id)
            if player is not self.owner:
                raise PlayerError("Only the game creator can start the game")
            if len(self.info.players) < 3:
                raise GameStateError("Not enough players have joined the game")
            if self.info.state != GameState.not_started:
                raise GameStateError("Game has already started")

            self.start_round()

    def start_round(self):
        with self.lock:
            self.info.state = GameState.writing_topic
            self.player_answers = {}
            self.info.unguessed_answers = []
            self.info.guessers_remaining = []
            self.info.guesser = None

            for player in self.info.players:
                player.answer = ""
                player.is_guessing = False
            self._select_next_topic_writer()

    def set_topic(self, player_id: str, topic: str):
        with self.lock:
            if self.info.state != GameState.writing_topic:
                raise GameStateError("Cannot set topic in this game state")
            player = self._find_player(player_id)
            if not player.is_topic_writer:
                raise PlayerError("Player is not topic writer, cannot set topic!")
            topic = topic.strip()
            if not topic:
                raise InputError("Topic writer did not provide a topic")
            self.info.current_topic = topic
            self.info.state = GameState.writing_answers

    def submit_answer(self, player_id: str, answer: str):
        with self.lock:
            if self.info.state != GameState.writing_answers:
                raise GameStateError("Cannot submit an answer in this game state")
            player = self._find_player(player_id)
            answer = answer.strip()
            if not answer:
                raise InputError("Player did not write an answer")
            self.player_answers[player] = answer

            if len(self.player_answers) == len(self.info.players):
                self.start_matching()

    def start_matching(self):
        with self.lock:
            self.info.state = GameState.matching
            self.info.unguessed_answers = self.player_answers.values()
            rand.shuffle(self.info.unguessed_answers)
            self._select_next_guesser()

    def submit_match(self, player_id, answer, guessed_player_id):
        player = self._find_player(player_id)
        guessed_player = self._find_player(guessed_player_id)
        answer = answer.strip()

        if not player.is_guessing:
            raise GameStateError("Player is not the current guesser!")
        if answer not in self.info.unguessed_answers:
            raise InputError(f"Answer '{answer}' is not in the current game")
        if player_id == guessed_player_id:
            raise InputError("Cannot guess yourself!")
        guessers_remaining = [p for p in self.info.players if not p.answer]
        if guessed_player not in guessers_remaining:
            raise GameStateError("Cannot guess a player that's not a remaining guesser")

        guessed_player_answer = self.player_answers.get(guessed_player, "")

        if answer != guessed_player_answer:
            self._select_next_guesser()
            return "", ""

        player.score += 1
        self.info.unguessed_answers.remove(answer)
        guessed_player.answer = guessed_player_answer

        if len(guessers_remaining) == 2:
            self.info.state = GameState.round_complete

        return guessed_player_id, guessed_player_answer
