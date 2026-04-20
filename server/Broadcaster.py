"""
Broadcaster.py — Async message fan-out to all connected clients.

Runs in its own daemon thread so network I/O never blocks the game loop.
"""

from threading import Thread, Lock
import queue

from shared.Protocol import send_object, MSG_STATE, MSG_WAVE_START, MSG_WAVE_CLEAR, MSG_GAME_OVER, MSG_GAME_WIN


class Broadcaster(Thread):
    def __init__(self, client_list, game_state):
        super().__init__(name="BroadcasterThread", daemon=True)
        self.client_list = client_list
        self.game_state = game_state
        self._send_lock = Lock()
        self.send_queue = queue.Queue()

        self._wire_callbacks()

    def run(self) -> None:
        print("[BROADCASTER] Thread started.")
        while True:
            try:
                func, args = self.send_queue.get(timeout=1.0)
                func(*args)
                self.send_queue.task_done()
            except queue.Empty:
                continue

    # ── Public interface (enqueue) ────────────────────────────────────────────

    def broadcast_state(self) -> None:
        """Enqueue the current game state for delivery to all clients."""
        state = self.game_state.to_dict()
        msg   = {"type": MSG_STATE, "state": state}
        self.send_queue.put((self._execute_broadcast, (msg,)))

    def broadcast(self, msg: dict) -> None:
        self.send_queue.put((self._execute_broadcast, (msg,)))

    # ── Internal execution (called by the thread) ─────────────────────────────

    def _execute_send(self, pc, msg: dict) -> None:
        if not pc.connected:
            return
        try:
            with self._send_lock:
                send_object(pc.conn, msg)
        except Exception:
            pc.connected = False

    def _execute_broadcast(self, msg: dict) -> None:
        for pc in self.client_list.get_all():
            self._execute_send(pc, msg)

    # ── Event callbacks ───────────────────────────────────────────────────────

    def _wire_callbacks(self) -> None:
        self.game_state.on_wave_start.connect(self.on_wave_start)
        self.game_state.on_wave_clear.connect(self.on_wave_clear)
        self.game_state.on_game_over.connect(self.on_game_over)
        self.game_state.on_game_win.connect(self.on_game_win)

    def on_wave_start(self, n: int) -> None:
        self.broadcast({"type": MSG_WAVE_START, "wave": n})

    def on_wave_clear(self, n: int) -> None:
        self.broadcast({"type": MSG_WAVE_CLEAR, "wave": n})

    def on_game_over(self) -> None:
        self.broadcast({"type": MSG_GAME_OVER})

    def on_game_win(self) -> None:
        self.broadcast({"type": MSG_GAME_WIN})