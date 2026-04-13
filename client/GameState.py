"""
GameState.py — Client-side mirror of server state.

Updated every time a MSG_STATE packet arrives.
Bullets are simulated locally from spawn/remove events — never sent in full.
"""

import time # usado para simular o movimento das balas entre atualizações do servidor
from shared.Constants import SCREEN_WIDTH, SCREEN_HEIGHT # usado para descartar balas que saem da tela


class LocalBullet:
    def __init__(self, d: dict):
        self.id = d["id"]
        self.x = float(d["x"])
        self.y = float(d["y"])
        self.vx = float(d["vx"])
        self.vy = float(d["vy"])
        self.owner = d.get("owner", "enemy")
        self.radius = d.get("radius", 6)
        self.damage = d.get("damage", 10)
        self.alive = True

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        m = self.radius
        if (self.x < -m or self.x > SCREEN_WIDTH  + m or self.y < -m or self.y > SCREEN_HEIGHT + m):
            self.alive = False

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "owner": self.owner, "radius": self.radius}


class ClientGameState:
    """
    Holds the last received server snapshot.
    Bullets are simulated locally between state updates.
    """

    def __init__(self):
        self.phase = "LOBBY"
        self.players = {}     # pid_str → player dict
        self.wave = {}     
        self.shop_remaining = 0.0

        # Local bullet simulation
        self._bullets: dict[str, LocalBullet] = {}   # id → LocalBullet
        self._last_sim_time = time.time()

        self.my_player_id: str | None = None

        # Event flags
        self.event_wave_start = False
        self.event_wave_clear = False
        self.event_shop_open = False
        self.event_shop_close = False
        self.event_game_over = False
        self.event_game_win = False
        self._wave_number_evt = 0

    # ── Update from server snapshot ───────────────────────────────────────────

    def apply_state(self, state: dict) -> None:
        self.phase = state.get("phase", self.phase)
        self.players = state.get("players", self.players)
        self.wave = state.get("wave", self.wave)
        self.shop_remaining = state.get("shop_remaining", 0.0)
        # bullets are NOT in state — managed via bullet_events

    def apply_bullet_events(self, spawn: list, remove: list) -> None:
        for bid in remove:
            self._bullets.pop(bid, None)
        for d in spawn:
            self._bullets[d["id"]] = LocalBullet(d)

    # ── Per-frame local simulation ────────────────────────────────────────────

    def simulate_bullets(self) -> None:
        """Call once per render frame to advance bullets locally."""
        now = time.time()
        dt = now - self._last_sim_time
        self._last_sim_time = now
        dead = []
        for bid, b in self._bullets.items():
            b.update(dt)
            if not b.alive:
                dead.append(bid)
        for bid in dead:
            del self._bullets[bid]

    @property
    def bullets(self) -> list:
        """Returns render-ready dicts for all live local bullets."""
        return [b.to_dict() for b in self._bullets.values()]

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