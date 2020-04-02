import string
from enum import Enum
import random


rand = random.SystemRandom()


def to_dict(obj):
    members = {}

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
        if name.startswith("_"):
            continue
        members[name] = convert(val)
    return members


def generate_id(length=6):
    return "".join([rand.choice(string.ascii_uppercase) for _ in range(length)])