import os
import string
from enum import Enum
import random
import secrets
import base64


rand = random.SystemRandom()

word_list = []


def _init_word_list():
    with open(os.path.join(os.path.dirname(__file__), "word_id_list.txt"), "r") as f:
        for line in f:
            line = line.strip()
            if line:
                word_list.append(line.upper())


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


def to_dict(obj, omit=None, replace=None):
    members = {}
    if omit is None:
        omit = []
    elif not isinstance(omit, (list, tuple)):
        omit = [omit]
    if replace is None or not isinstance(replace, dict):
        replace = {}

    def convert(value):
        if hasattr(value, "to_dict"):
            return value.to_dict()
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, (list, tuple)):
            return [convert(v) for v in value]
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}
        return value

    for name, val in obj.__dict__.items():
        if name.startswith("_") or name in omit:
            continue
        if name in replace:
            members[name] = replace[name]
        else:
            members[name] = convert(val)
    return members


def generate_game_id():
    if not word_list:
        _init_word_list()
    return rand.choice(word_list)


def generate_id(length=6):
    return "".join([rand.choice(string.ascii_uppercase) for _ in range(length)])


def generate_key(length=64):
    return base64.b64encode(secrets.token_bytes(length)).decode("utf8")