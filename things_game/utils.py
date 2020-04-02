import string
import secrets



def generate_id(length=6):
    return "".join([secrets.choice(string.ascii_uppercase) for _ in range(length)])


