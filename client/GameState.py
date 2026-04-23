"""
GameState.py — Client-side mirror of the server state.

Updated every time a MSG_STATE packet arrives.
Event flags are set by comparing the incoming phase to the previous one.
"""


class ClientGameState:
    def __init__(self):
        self.phase = "LOBBY"
        self.players: dict = {}
        self.wave: dict = {}
        self.bullets: list = []
        self.my_player_id = None

        # One-shot event flags consumed by the main loop
        self.event_wave_clear = False
        self.event_game_over = False
        self.event_game_win = False

    def apply_state(self, state: dict) -> None:
        incoming_phase = state.get("phase", self.phase)

        # Set one-shot flags on phase transitions
        if incoming_phase != self.phase:
            if incoming_phase == "WAVE_CLEAR":
                self.event_wave_clear = True
            elif incoming_phase == "GAMEOVER":
                self.event_game_over = True
            elif incoming_phase == "WIN":
                self.event_game_win = True

        self.phase = incoming_phase
        self.players = state.get("players", self.players)
        self.wave = state.get("wave",    self.wave)
        self.bullets = state.get("bullets", [])

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