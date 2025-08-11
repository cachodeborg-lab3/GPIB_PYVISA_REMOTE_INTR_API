import json

with open("config.json") as f:
    CONFIG = json.load(f)

TOKENS = {v["token"]: k for k, v in CONFIG["users"].items()}

def verify_token(token):
    return TOKENS.get(token)

def get_permissions(token):
    username = verify_token(token)
    if username:
        return CONFIG["users"][username]["permissions"]
    return None
