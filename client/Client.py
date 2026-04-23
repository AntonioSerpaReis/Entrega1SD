"""
Client.py — TCP connection wrapper and send helper.
"""

import socket
import threading

from shared.Protocol import send_object
from client.GameState import ClientGameState
from client.Receiver import Receiver


class Client:
    def __init__(self, host: str, port: int, game_state: ClientGameState):
        self.host = host
        self.port = port
        self._sock: socket.socket | None = None
        self._receiver: Receiver | None  = None
        self._send_lock = threading.Lock()
        self.gs = game_state
        self.error_msg = None

    def connect(self) -> bool:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._sock.connect((self.host, self.port))
            self._receiver = Receiver(self._sock, self.gs)
            return True
        except socket.error as e:
            self.error_msg = str(e)
            return False

    def start_recv_thread(self) -> None:
        if self._receiver:
            self._receiver.start()

    def disconnect(self) -> None:
        if self._receiver:
            self._receiver.stop()
        if self._sock:
            try:
                self._sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self._sock.close()

    @property
    def connected(self) -> bool:
        return self._receiver.is_alive() if self._receiver else False

    def send(self, msg: dict) -> bool:
        if not self.connected or not self._sock:
            return False
        with self._send_lock:
            try:
                send_object(self._sock, msg)
                return True
            except (socket.error, BrokenPipeError):
                if self._receiver:
                    self._receiver.stop()
                return False