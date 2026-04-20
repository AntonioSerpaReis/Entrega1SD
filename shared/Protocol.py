"""
Protocol.py — Message types and serialization helpers.

All messages are JSON-encoded dicts with a top-level "type" key.
"""

import json

# ── Message type constants ────────────────────────────────────────────────────

# Variable size
INT_SIZE = 8

# Client → Server
MSG_JOIN        = "join"         # {"type":"join","name":"Alice","class_id":2}
MSG_INPUT       = "input"        # {"type":"input","keys":{...},"mouse":{...}}

# Server → Client
MSG_WELCOME = "welcome"        # {"type":"welcome","player_id":0,"state":{...}}
MSG_STATE = "state"          # {"type":"state","state":{...}}
MSG_BULLET_EVENTS = "bullet_events"  # {"type":"bullet_events","spawn":[...],"remove":[...]}
MSG_WAVE_START = "wave_start"     # {"type":"wave_start","wave":2}
MSG_WAVE_CLEAR = "wave_clear"     # {"type":"wave_clear","wave":2}
MSG_GAME_OVER = "game_over"      # {"type":"game_over"}
MSG_GAME_WIN = "game_win"       # {"type":"game_win"}
MSG_ERROR = "error"          # {"type":"error","msg":"..."}

# ── Serialization helpers ─────────────────────────────────────────────────────

def receive_int(connection) -> int:
    """
    :param n_bytes: The number of bytes to read from the current connection
    :return: The next integer read from the current connection
    """
    data = connection.recv(INT_SIZE)
    return int.from_bytes(data, byteorder='big', signed=True)

def send_int(connection, value: int) -> None:
    """
    :param value: The integer value to be sent to the current connection
    :param n_bytes: The number of bytes to send
    """
    connection.send(value.to_bytes(INT_SIZE, byteorder="big", signed=True))

def send_object(connection, obj):
    """1º: envia tamanho, 2º: envia dados."""
    data = json.dumps(obj).encode('utf-8')
    size = len(data)
    send_int(connection, size)    
    connection.send(data)              		     

def receive_object(connection):
    """1º: lê tamanho, 2º: lê dados."""
    size = receive_int(connection)
    data = b""
    while len(data) < size:
        chunk = connection.recv(size - len(data))
        data += chunk
    result = json.loads(data.decode('utf-8'))
    return result