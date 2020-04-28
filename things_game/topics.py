import time
import os
import threading
import random


DEFAULT_FILE = os.path.join(os.path.dirname(__file__), "topics.txt")
T_MIN_CHECK_INTERVAL_S = 15*60


class TopicsList(object):
    def __init__(self, topics_file=None):
        if not topics_file:
            topics_file = DEFAULT_FILE
        if not os.path.isfile(topics_file):
            raise ValueError(f"Topics file must exist on disk. Unable to find '{topics_file}'")
        self._topics_filename = topics_file
        self._lock = threading.RLock()
        self._topics = []
        self._t_last_load = 0

    def _load_list_from_file(self):
        with self._lock:
            with open(self._topics_filename, "r") as f:
                self._topics = [line.strip() for line in f if line.strip()]
            self._t_last_load = int(time.time())

    def _check_list_updated(self):
        with self._lock:
            if time.time() - self._t_last_load < T_MIN_CHECK_INTERVAL_S:
                return
            f_update_time = os.stat(self._topics_filename).st_mtime
            if f_update_time > self._t_last_load:
                self._load_list_from_file()

    def get_random_topic(self):
        self._check_list_updated()
        with self._lock:
            return random.choice(self._topics)
