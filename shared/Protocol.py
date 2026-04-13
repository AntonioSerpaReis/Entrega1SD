"""
Protocol.py — Message types and serialization helpers.

All messages are JSON-encoded dicts with a top-level "type" key.
"""

import json

# ── Message type constants ────────────────────────────────────────────────────

# Client → Server
MSG_JOIN        = "join"         # {"type":"join","name":"Alice","class_id":2}
MSG_INPUT       = "input"        # {"type":"input","keys":{...},"mouse":{...}}
MSG_BUY_UPGRADE = "buy_upgrade"  # {"type":"buy_upgrade","upgrade":"damage"}

# Server → Client
MSG_WELCOME       = "welcome"        # {"type":"welcome","player_id":0,"state":{...}}
MSG_STATE         = "state"          # {"type":"state","state":{...}}
MSG_BULLET_EVENTS = "bullet_events"  # {"type":"bullet_events","spawn":[...],"remove":[...]}
MSG_WAVE_START    = "wave_start"     # {"type":"wave_start","wave":2}
MSG_WAVE_CLEAR    = "wave_clear"     # {"type":"wave_clear","wave":2}
MSG_SHOP_OPEN     = "shop_open"      # {"type":"shop_open"}
MSG_SHOP_CLOSE    = "shop_close"     # {"type":"shop_close"}
MSG_GAME_OVER     = "game_over"      # {"type":"game_over"}
MSG_GAME_WIN      = "game_win"       # {"type":"game_win"}
MSG_ERROR         = "error"          # {"type":"error","msg":"..."}

# ── Serialization helpers ─────────────────────────────────────────────────────

def encode(msg: dict) -> bytes:
    """Serialize a message dict to bytes."""
    return (json.dumps(msg) + "\n").encode("utf-8")

def decode(data: bytes) -> list[dict]:
    """
    Decode one or more newline-delimited JSON frames from raw bytes.
    Returns a list of parsed dicts (may be empty if data is incomplete).
    """
    messages = []
    for line in data.split(b"\n"):
        line = line.strip()
        if not line:
            continue
        try:
            messages.append(json.loads(line.decode("utf-8")))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    return messages

def make_input(keys: dict, mouse_x: float, mouse_y: float, mouse_btn: bool, ability: bool) -> dict:
    return {
        "type": MSG_INPUT,
        "keys": keys,
        "mouse": {"x": mouse_x, "y": mouse_y, "btn": mouse_btn},
        "ability": ability,
    }

def make_join(class_id: int) -> dict:
    return {"type": MSG_JOIN, "class_id": class_id}

def make_buy_upgrade(upgrade: str) -> dict:
    return {"type": MSG_BUY_UPGRADE, "upgrade": upgrade}