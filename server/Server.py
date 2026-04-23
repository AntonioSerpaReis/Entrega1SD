"""
Server.py — Entry point for the game server.

Starts the accept loop in a background thread and runs the game loop
on the main thread.
"""

import socket
import time

from shared.Constants import SERVER_PORT, MAX_PLAYERS, TICK_RATE
from server.GameState import GameState
from server.ProcessClient import ProcessClient
from server.Broadcaster import Broadcaster
from server.ClientList import ClientList


class Server:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(("", SERVER_PORT))
        self._socket.listen(MAX_PLAYERS)
        self._socket.setblocking(False)

        self._game_state = GameState()
        self._clients = ClientList()
        self._broadcaster = Broadcaster(self._clients, self._game_state, 1/TICK_RATE)

        self._running = False

    def _interrupt_for_clients(self) -> None:
        """
        Breaks the game loop flow to check if a client is waiting.
        If found, it accepts them and starts their handler thread.
        """
        try:
            conn, addr = self._socket.accept()

            print(f"[SERVER] Loop interrupted: Player joining from {addr}")           
            
            # Start the client handler thread
            ProcessClient(conn, addr, self._game_state, self._clients).start()
            
        except (socket.timeout, BlockingIOError):
            # No one is waiting; no interruption needed
            pass

    def run(self) -> None:
        self._running = True
        self._broadcaster.start()
        print(f"[SERVER] Main loop running. Listening for interrupts on {SERVER_PORT}...")
        self._run_game_loop()

    def _run_game_loop(self) -> None:
        tick_interval = 1.0 / TICK_RATE
        last_time = time.time()

        while self._running:
            start_tick = time.time()
            dt = start_tick - last_time
            last_time = start_tick

            # THE BREAK: Check for new players right now
            self._interrupt_for_clients()

            # THE GAME: Run logic update
            self._game_state.update(dt)

            # THE TIMING: Wait for next tick
            elapsed = time.time() - start_tick
            time.sleep(max(0, tick_interval - elapsed))