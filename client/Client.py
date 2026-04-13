"""
Client.py — Manages the TCP connection to the server.

Runs a receive thread that feeds incoming messages into the shared
ClientGameState.  The main thread calls send() to push input frames.
"""

import socket
import threading

from shared.Protocol import (encode, decode,
                               MSG_WELCOME, MSG_STATE, MSG_BULLET_EVENTS,
                               MSG_WAVE_START, MSG_WAVE_CLEAR,
                               MSG_SHOP_OPEN, MSG_SHOP_CLOSE,
                               MSG_GAME_OVER, MSG_GAME_WIN,
                               MSG_ERROR) # usado em _handle()
from client.GameState import ClientGameState # usado para atualizar o estado do jogo com as mensagens recebidas


class Client:
    """
    Owns the socket and a receive daemon thread.
    Call connect() before start(); call disconnect() on exit.
    """

    def __init__(self, host: str, port: int, game_state: ClientGameState):
        self.host = host
        self.port = port
        self.gs = game_state

        self._sock: socket.socket | None = None
        self._recv_thread: threading.Thread | None = None
        self._recv_buf = b""
        self._connected = False
        self._send_lock = threading.Lock()

        self.on_welcome = None
        self.error_msg = None

    # ── Connect / disconnect ──────────────────────────────────────────────────

    def connect(self) -> bool:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(5.0)
        try:
            self._sock.connect((self.host, self.port))
            self._connected = True
            return True
        except socket.error as e:
            print(f"[Client] Connection error: {e}")
            self.error_msg = str(e)
            return False


    def start_recv_thread(self) -> None:
        self._recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._recv_thread.start()

    def disconnect(self) -> None:
        self._connected = False
        if self._sock:
            self._sock.close()


    @property
    def connected(self) -> bool:
        return self._connected

    # ── Send ──────────────────────────────────────────────────────────────────

    def send(self, msg: dict) -> bool:
        if not self._connected or not self._sock:
            return False
        with self._send_lock:
            self._sock.sendall(encode(msg))
        return True

    # ── Receive loop ──────────────────────────────────────────────────────────

    def _recv_loop(self) -> None:
        while self._connected:
            if not self._sock:
                break
            chunk = self._sock.recv(512)
            if not chunk:
                break
            self._recv_buf += chunk
            self._process_buffer()

        self._connected = False

    def _process_buffer(self) -> None:
        chunks = self._recv_buf.split(b"\n")
        self._recv_buf = chunks.pop()
        for chunk in chunks:
            if not chunk:
                continue
            decoded_messages = decode(chunk + b"\n") 
            
            for msg in decoded_messages:
                self._handle(msg)

    def _handle(self, msg: dict) -> None:
        mtype = msg.get("type")

        if mtype == MSG_WELCOME:
            pid = msg.get("player_id")
            self.gs.my_player_id = pid
            state = msg.get("state", {})
            if state:
                self.gs.apply_state(state)
            if self.on_welcome:
                self.on_welcome(pid)

        elif mtype == MSG_STATE:
            self.gs.apply_state(msg.get("state", {}))

        elif mtype == MSG_BULLET_EVENTS:
            self.gs.apply_bullet_events(msg.get("spawn",  []), msg.get("remove", []))

        elif mtype == MSG_WAVE_START:
            self.gs.event_wave_start = True
            self.gs._wave_number_evt = msg.get("wave", 0)

        elif mtype == MSG_WAVE_CLEAR:
            self.gs.event_wave_clear = True

        elif mtype == MSG_SHOP_OPEN:
            self.gs.event_shop_open = True

        elif mtype == MSG_SHOP_CLOSE:
            self.gs.event_shop_close = True

        elif mtype == MSG_GAME_OVER:
            self.gs.event_game_over = True

        elif mtype == MSG_GAME_WIN:
            self.gs.event_game_win = True

        elif mtype == MSG_ERROR:
            print(f"[Client] Server error: {msg.get('msg')}")