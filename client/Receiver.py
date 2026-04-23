"""
Receiver.py — Background thread that reads and dispatches server messages.
"""

import socket
import threading

from shared.Protocol import (
    receive_object,
    MSG_WELCOME, MSG_STATE
)


class Receiver(threading.Thread):
    def __init__(self, sock: socket.socket, game_state):
        super().__init__(daemon=True)
        self._sock = sock
        self.gs = game_state

    def stop(self) -> None:
        pass  # socket closure from Client.disconnect() will unblock recv

    def run(self) -> None:
        while True:
            try:
                msg = receive_object(self._sock)
                if msg is None:
                    break
                self._process(msg)
            except Exception as e:
                print(f"[Receiver] Disconnected: {e}")
                break

    def _process(self, msg: dict) -> None:
        mtype = msg.get("type")

        if mtype == MSG_WELCOME:
            self.gs.my_player_id = msg.get("player_id")
            state = msg.get("state", {})
            if state:
                self.gs.apply_state(state)

        elif mtype == MSG_STATE:
            self.gs.apply_state(msg.get("state", {}))