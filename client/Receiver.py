"""
Receiver.py — Background thread that reads and dispatches server messages.
"""

import socket
import threading

from shared.Protocol import (
    receive_object,
    MSG_WELCOME, MSG_STATE, MSG_BULLET_EVENTS,
    MSG_WAVE_START, MSG_WAVE_CLEAR,
    MSG_GAME_OVER, MSG_GAME_WIN, MSG_ERROR,
)


class Receiver(threading.Thread):
    def __init__(self, sock: socket.socket, game_state):
        super().__init__(daemon=True)
        self._sock = sock
        self.gs    = game_state

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

        elif mtype == MSG_BULLET_EVENTS:
            self.gs.apply_bullet_events(msg.get("spawn", []), msg.get("remove", []))

        elif mtype == MSG_WAVE_START:
            self.gs.event_wave_start = True

        elif mtype == MSG_WAVE_CLEAR:
            self.gs.event_wave_clear = True

        elif mtype == MSG_GAME_OVER:
            self.gs.event_game_over = True

        elif mtype == MSG_GAME_WIN:
            self.gs.event_game_win = True

        elif mtype == MSG_ERROR:
            print(f"[Client] Server error: {msg.get('msg')}")