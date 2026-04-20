"""
GameState.py — Client-side mirror of the server state.

Updated every time a MSG_STATE packet arrives.
"""


class ClientGameState:
    def __init__(self):
        self.phase        = "LOBBY"
        self.players: dict = {}
        self.wave:    dict = {}
        self.bullets: list = []
        self.my_player_id = None

        # One-shot event flags consumed by the main loop
        self.event_wave_start = False
        self.event_wave_clear = False
        self.event_game_over  = False
        self.event_game_win   = False

    def apply_state(self, state: dict) -> None:
        self.phase   = state.get("phase",   self.phase)
        self.players = state.get("players", self.players)
        self.wave    = state.get("wave",    self.wave)
        self.bullets = state.get("bullets", [])

    def apply_bullet_events(self, spawn: list, remove: list) -> None:
        existing = {b["id"]: b for b in self.bullets}
        for b in spawn:
            existing[b["id"]] = b
        for bid in remove:
            existing.pop(bid, None)
        self.bullets = list(existing.values())

    # ── Convenience accessors ─────────────────────────────────────────────────

    @property
    def my_player(self) -> dict | None:
        if self.my_player_id is None:
            return None
        return self.players.get(str(self.my_player_id))

    @property
    def wave_number(self) -> int:
        return self.wave.get("wave_number", 0)

    @property
    def wave_state(self) -> str:
        return self.wave.get("state", "WAITING")

    @property
    def enemies(self) -> list:
        return self.wave.get("enemies", [])