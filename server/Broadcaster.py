from threading import Lock, Thread
from time import sleep
from server import ClientList, GameState, send_object, MSG_STATE


class Broadcaster(Thread):
    def __init__(self, client_list: ClientList, game_state: GameState, interval: float):
        super().__init__(daemon=True)
        self.client_list: ClientList = client_list
        self.game_state: GameState = game_state
        self.interval: float = interval
        self._send_lock: Lock = Lock()

    def broadcast_state(self) -> None:
        msg = {"type": MSG_STATE, "state": self.game_state.to_dict()}
        for pc in self.client_list.get_all():
            if not pc.connected:
                continue
            try:
                with self._send_lock:
                    send_object(pc.conn, msg)
            except Exception:
                pc.connected = False

    def run(self):
        while True:
            self.broadcast_state()
            sleep(self.interval)