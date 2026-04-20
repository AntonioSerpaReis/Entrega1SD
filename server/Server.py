"""
Server.py — Entry point for the game server.

Starts the accept loop in a background thread and runs the game loop
on the main thread.
"""

import socket
import threading
import time

from shared.Constants import SERVER_HOST, SERVER_PORT, MAX_PLAYERS, TICK_RATE
from server.GameState import GameState
from server.ProcessClient import ProcessClient
from server.Broadcaster import Broadcaster
from server.ClientList import ClientList


class Server:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(("", SERVER_PORT))
        self._socket.listen(MAX_PLAYERS)

        self._game_state = GameState()
        self._clients = ClientList()
        self._broadcaster = Broadcaster(self._clients, self._game_state)
        self._broadcaster.start()

        self._running = False

    def run(self) -> None:
        self._running = True
        threading.Thread(target=self._accept_loop, args=(self._socket,), daemon=True).start()
        print(f"[SERVER] Listening on {SERVER_HOST}:{SERVER_PORT}")
        self._run_game_loop()

    def _accept_loop(self, sock: socket.socket) -> None:
        while self._running:
            try:
                conn, addr = sock.accept()
                print(f"[SERVER] New connection from {addr}")
                ProcessClient(conn, addr, self._game_state, self._clients).start()
            except Exception as e:
                if self._running:
                    print(f"[SERVER] Accept error: {e}")
                break

    def _run_game_loop(self) -> None:
        tick_interval = 1.0 / TICK_RATE
        last_time = time.time()

        while self._running:
            start_tick = time.time()
            dt = start_tick - last_time
            last_time = start_tick

            self._game_state.update(dt)
            self._broadcaster.broadcast_state()

            elapsed = time.time() - start_tick
            time.sleep(max(0, tick_interval - elapsed))