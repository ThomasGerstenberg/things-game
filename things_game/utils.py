import string
from enum import Enum
import random
import secrets
import base64


rand = random.SystemRandom()


def to_dict(obj, omit=None):
    members = {}
    if omit is None:
        omit = []
    elif not isinstance(omit, (list, tuple)):
        omit = [omit]

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
        members[name] = convert(val)
    return members


def generate_id(length=6):
    return "".join([rand.choice(string.ascii_uppercase) for _ in range(length)])


def generate_key(length=64):
    return base64.b64encode(secrets.token_bytes(length)).decode("utf8")