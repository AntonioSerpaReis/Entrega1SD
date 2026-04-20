"""
ClientList.py — Thread-safe registry of active ProcessClient connections.
"""

import threading


class ClientList:
    def __init__(self):
        self._clients: dict = {}
        self._lock = threading.Lock()

    def add(self, player_id, pc) -> None:
        with self._lock:
            self._clients[player_id] = pc

    def remove(self, player_id) -> None:
        with self._lock:
            self._clients.pop(player_id, None)

    def get_all(self) -> list:
        """Return a snapshot of current clients to avoid race conditions."""
        with self._lock:
            return list(self._clients.values())

    def get_lock(self) -> threading.Lock:
        return self._lock

    def get_dict(self) -> dict:
        return self._clients

    def __len__(self) -> int:
        with self._lock:
            return len(self._clients)