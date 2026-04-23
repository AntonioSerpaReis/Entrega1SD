"""
ProcessClient.py — Dedicated thread for one connected client.

Owns the blocking recv() loop and routes incoming messages to GameState.
"""

import socket
import threading
import json

from shared.Protocol import send_object, receive_object, MSG_INPUT, MSG_JOIN, MSG_WELCOME


class ProcessClient(threading.Thread):
    def __init__(self, conn: socket.socket, addr: tuple, game_state, client_list):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr
        self.player_id = None
        self.game_state = game_state
        self.clients = client_list
        self.connected = True

    # ── Thread loop ───────────────────────────────────────────────────────────

    def run(self) -> None:
        self.conn.settimeout(None)
        try:
            while self.connected:
                msg = receive_object(self.conn)
                
                if msg is None:
                    break

                self._route(msg)

        except (ConnectionResetError, EOFError, json.JSONDecodeError):
            pass

        self._cleanup()

    # ── Disconnect ────────────────────────────────────────────────────────────

    def _cleanup(self) -> None:
        self.connected = False
        if self.player_id:
            self.clients.remove(self.player_id)
            self.game_state.remove_player(self.player_id)
        self.conn.close()

    # ── Message routing ───────────────────────────────────────────────────────

    def _route(self, msg: dict) -> None:
        mtype = msg.get("type")
        if mtype == MSG_JOIN:
            self._handle_join()
        elif mtype == MSG_INPUT:
            self._apply_input(msg)

    def _apply_input(self, msg: dict) -> None:
        if self.player_id is None:
            return
        player = self.game_state.players.get(self.player_id)
        if player:
            keys = msg.get("keys", {})
            player.latest_input = {
                k: bool(keys.get(k, False))
                for k in ["up", "down", "left", "right",
                          "attack_up", "attack_down", "attack_left", "attack_right"]
            }

    def _handle_join(self) -> None:
        pid = f"{self.addr[0]}:{self.addr[1]}"
        self.player_id = pid

        self.clients.add(pid, self)
        self.game_state.add_player(pid)

        welcome = {
            "type": MSG_WELCOME,
            "player_id": pid,
            "state": self.game_state.to_dict(),
        }
        try:
            send_object(self.conn, welcome)
        except Exception as e:
            print(f"[ProcessClient] Failed to send welcome: {e}")
            self.connected = False