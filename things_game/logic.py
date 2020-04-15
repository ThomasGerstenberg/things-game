from typing import List, Optional, Dict
from enum import Enum
import random
import time
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
    def __init__(self, name, player_id="", is_observer=False, is_owner=False, color="blue"):
        self.name = name
        self.id = player_id or generate_id()
        self.session_key = generate_key()
        self.is_observer = is_observer
        self.is_owner = is_owner
        self.is_topic_writer = False
        self.is_guessing = False
        self.submitted_answer = False
        self.answer = ""
        self.score = 0
        self.color = color

    def to_dict(self):
        return to_dict(self, omit="session_key")

    def __eq__(self, other):
        if not isinstance(other, Player):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class Answer(object):
    def __init__(self, answer_id, player, text):
        self.id = answer_id
        self.text = text
        self.player = player
        self.matched = False

    def to_dict(self):
        omit = None if self.matched else "player"
        return to_dict(self, omit)

    def __eq__(self, other):
        if not isinstance(other, Answer):
            return False
        return self.id == other.id


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
        self.answers: List[Answer] = []

    def to_dict(self):
        replace = dict(answers=[])
        if self.state in [GameState.matching, GameState.round_complete]:
            replace = None
        return to_dict(self, replace=replace)

    def find_answer(self, answer_id):
        for a in self.answers:
            if a.id == answer_id:
                return a
        return None

    def remove_answer(self, player):
        for a in self.answers:
            if player == a.player:
                self.answers.remove(a)
                return

    def reveal_all_answers(self):
        for a in self.answers:
            a.matched = True

    def get_guessers(self):
        return [p for p in self.players if p.submitted_answer and p.answer]

    def next_player(self, player: Player, player_list: List[Player] = None):
        if player_list is None:
            player_list = self.players
        if player in player_list:
            index_next = player_list.index(player) + 1
        else:
            index_next = 1
        return player_list[index_next % len(player_list)]

    def next_guesser(self):
        guessers = self.get_guessers()
        if not self.guesser:
            self.guesser = self.next_player(self.topic_writer, guessers)
        else:
            self.guesser.is_guessing = False
            self.guesser = self.next_player(self.guesser, guessers)
        self.guesser.is_guessing = True

    def next_topic_writer(self):
        if not self.topic_writer:
            self.topic_writer = rand.choice(self.players)
        else:
            self.topic_writer.is_topic_writer = False
            self.topic_writer = self.next_player(self.topic_writer)
        self.topic_writer.is_topic_writer = True

    def __eq__(self, other):
        if not isinstance(other, GameInfo):
            return False
        return self.game_id == other.game_id


class ThingsGame(object):
    def __init__(self, name, password_hash="", salt="", game_id="", score_limit=11):
        self.info = GameInfo(name, game_id or generate_id(), score_limit)
        self.password = password_hash
        self.salt = salt
        self.create_time = time.time()
        self.last_update_time = time.time()
        self.owner: Optional[Player] = None
        self.lock = RLock()
        self.matching = False

    @property
    def id(self):
        return self.info.game_id

    def to_dict(self):
        return self.info.to_dict()

    def _generate_id(self, id_list):
        item_id = generate_id()
        while item_id in id_list:
            item_id = generate_id()
        return item_id

    def _generate_player_id(self):
        return self._generate_id([p.id for p in self.info.players + self.info.observers])

    def _generate_answer_id(self):
        return self._generate_id([a.id for a in self.info.answers])

    def _find_player(self, player_id, player_list: List[Player] = None):
        if player_list is None:
            player_list = self.info.players

        for p in player_list:
            if player_id == p.id:
                return p
        return PlayerError(f"Unable to find player with id {player_id}")

    def _updated(self):
        with self.lock:
            self.last_update_time = time.time()

    def add_player(self, name, is_observer, color="blue"):
        self._updated()
        with self.lock:
            player_id = self._generate_player_id()

            player = Player(name, player_id, is_observer, not self.info.players, color)
            if is_observer:
                self.info.observers.append(player)
            else:
                self.info.players.append(player)
            return player

    def force_remove_player(self, owner_id, owner_session_key, player_id):
        with self.lock:
            self.validate_player(owner_id, owner_session_key, can_be_observer=True, must_be_owner=True)
            player = self._find_player(player_id, self.info.players + self.info.observers)
            self._remove_player(player)
            return player

    def remove_player(self, player_id, session_key):
        with self.lock:
            player = self.validate_player(player_id, session_key, can_be_observer=True)
            self._remove_player(player)
            return player

    def _remove_player(self, player: Player):
        if player.is_observer:
            self.info.observers.remove(player)
            return
        if self.info.state == GameState.writing_topic:
            if self.info.topic_writer == player:
                self.info.next_topic_writer()
            self.info.players.remove(player)
        elif self.info.state == GameState.writing_answers:
            self.info.remove_answer(player)
            self.info.players.remove(player)
            if len(self.info.answers) == len(self.info.players):
                self.start_matching()
        elif self.info.state == GameState.matching:
            self.info.remove_answer(player)
            guessers_remaining = self.info.get_guessers()
            if player in guessers_remaining:
                if len(guessers_remaining) <= 2:
                    self.info.guesser.score += 2
                    self.info.state = GameState.round_complete
                elif player is self.info.guesser:
                    self.info.next_guesser()
            self.info.players.remove(player)
        else:
            self.info.players.remove(player)

        if player.is_owner and self.info.players:
            self.info.players[0].is_owner = True
        return player

    def validate_player(self, player_id, session_key, can_be_observer=False,
                        must_be_owner=False, must_be_topic_writer=False, must_be_guessing=False):
        with self.lock:
            players = self.info.players[:]
            if can_be_observer:
                players.extend(self.info.observers[:])
            player = self._find_player(player_id, players)
            if player.session_key != session_key:
                raise PlayerError("Invalid session key for player")
            if must_be_owner and not player.is_owner:
                raise PlayerError("Must be game owner to perform this action")
            if must_be_topic_writer and not player.is_topic_writer:
                raise PlayerError("Player is not the topic writer")
            if must_be_guessing and not player.is_guessing:
                raise PlayerError("Player is not guessing")
            return player

    def start_game(self, player_id, session_key):
        self._updated()
        with self.lock:
            self.validate_player(player_id, session_key, can_be_observer=True, must_be_owner=True)
            if len(self.info.players) < 3:
                raise GameStateError("Not enough players have joined the game")
            if self.info.state != GameState.not_started:
                raise GameStateError("Game has already started")

            self.start_round()

    def reset_points(self, player_id, session_key):
        self._updated()
        with self.lock:
            self.validate_player(player_id, session_key, can_be_observer=True, must_be_owner=True)
            for p in self.info.players:
                p.score = 0

    def start_round(self):
        self._updated()
        with self.lock:
            self.info.state = GameState.writing_topic
            self.player_answers = {}
            self.info.answers = []
            self.info.guesser = None
            self.info.current_topic = ""

            for player in self.info.players:
                player.answer = ""
                player.submitted_answer = False
                player.is_guessing = False
            self.info.next_topic_writer()

    def set_topic(self, player_id: str, session_key: str, topic: str):
        self._updated()
        with self.lock:
            if self.info.state != GameState.writing_topic:
                raise GameStateError("Cannot set topic in this game state")
            player = self.validate_player(player_id, session_key, must_be_topic_writer=True)
            topic = topic.strip()
            if not topic:
                raise InputError("Topic writer did not provide a topic")
            self.info.current_topic = topic
            self.info.state = GameState.writing_answers

    def submit_answer(self, player_id: str, session_key: str, answer: str):
        self._updated()
        with self.lock:
            if self.matching:
                raise GameStateError("Already in the process of matching")
            if self.info.state != GameState.writing_answers:
                raise GameStateError("Cannot submit an answer in this game state")
            player = self.validate_player(player_id, session_key)
            answer = answer.strip()
            if not answer:
                raise InputError("Player did not write an answer")
            if len(answer) > 1:
                answer = answer[0].upper() + answer[1:]
            else:
                answer = answer.upper()

            updated = False
            # See if the user already answered, if so update that instead
            for a in self.info.answers:
                if a.player == player:
                    a.text = answer
                    updated = True
                    break

            if not updated:
                self.info.answers.append(Answer(self._generate_answer_id(), player, answer))

            player.submitted_answer = True

            if len(self.info.answers) == len(self.info.players):
                self.start_matching()

    def start_matching(self):
        self._updated()
        with self.lock:
            rand.shuffle(self.info.answers)
            self.info.next_guesser()
            self.info.state = GameState.matching

    def validate_match(self, player_id, session_key, answer_id, guessed_player_id):
        self._updated()
        with self.lock:
            if self.matching:
                raise GameStateError("Already in the process of performing a match")
            if self.info.state != GameState.matching:
                raise GameStateError("Incorrect game state: not currently matching answers")
            player = self.validate_player(player_id, session_key, must_be_guessing=True)
            guessed_player = self._find_player(guessed_player_id)

            if player_id == guessed_player_id:
                raise InputError("Cannot guess yourself!")

            # Get the list of guessers remaining
            guessers = self.info.get_guessers()
            # Find the answer based on the ID
            guessed_answer = self.info.find_answer(answer_id)
            if not guessed_answer:
                raise InputError(f"Answer '{answer_id}' is not in the current game")
            if guessed_player not in guessers:
                raise GameStateError("Cannot guess a player that's not a remaining guesser")

            guessed_player_answer = None
            for a in self.info.answers:
                if a.player == guessed_player:
                    guessed_player_answer = a
                    break
            if not guessed_player_answer:
                raise GameStateError("Unable to find guessed player's answer")
            self.matching = True
            return player, guessed_answer, guessed_player_answer

    def finalize_match(self, player: Player, guessed_answer: Answer, guessed_player_answer: Answer):
        self._updated()
        with self.lock:
            self.matching = False
            if guessed_answer != guessed_player_answer:
                self.info.next_guesser()
                return False

            player.score += 1
            guessed_player_answer.player.answer = guessed_player_answer.text
            guessed_player_answer.matched = True

            if len(self.info.get_guessers()) == 1:
                player.score += 1
                self.info.state = GameState.round_complete
                self.info.reveal_all_answers()

            return True
