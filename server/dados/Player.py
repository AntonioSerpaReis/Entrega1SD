"""
Player.py — Server-side player model.
"""

from shared.Constants import BULLET_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT
from server.dados.Bullet import Bullet


class Player:
    """Authoritative server-side player. All velocities in units/second."""

    FIRE_RATE = 0.18  # minimum seconds between shots

    def __init__(self, player_id: str, spawn_x: float, spawn_y: float):
        self.player_id = player_id
        self.x = spawn_x
        self.y = spawn_y
        self.speed = 5
        self.alive = True

        self.fire_cd_end = 0.0
        self.last_vx = 1.0
        self.last_vy = 0.0

        # Populated before the first tick so the initial update never KeyErrors
        self.latest_input = {
            "up": False, "down": False, "left": False, "right": False,
            "attack_up": False, "attack_down": False,
            "attack_left": False, "attack_right": False,
        }

    def update(self, dt: float, keys: dict, now: float) -> list[Bullet]:
        if not self.alive:
            return []
        self._move(dt, keys)
        return self._shoot(keys, now)

    def _move(self, dt: float, keys: dict) -> None:
        dx, dy = 0.0, 0.0

        if keys.get("up"): dy = -1
        elif keys.get("down"): dy =  1
        elif keys.get("left"): dx = -1
        elif keys.get("right"): dx =  1

        if dx != 0 or dy != 0:
            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt
            self.last_vx, self.last_vy = dx, dy

        self._clamp()

    def _clamp(self) -> None:
        self.x = max(0, min(SCREEN_WIDTH  - 1, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - 1, self.y))

    def _shoot(self, keys: dict, now: float) -> list[Bullet]:
        if now < self.fire_cd_end:
            return []

        svx, svy  = 0.0, 0.0
        firing    = False

        if keys.get("attack_up"): svy = -1; firing = True
        if keys.get("attack_down"):  svy =  1; firing = True
        if keys.get("attack_left"):  svx = -1; firing = True
        if keys.get("attack_right"): svx =  1; firing = True

        if not firing:
            return []

        self.fire_cd_end = now + self.FIRE_RATE
        return [Bullet(self.x, self.y, svx * BULLET_SPEED, svy * BULLET_SPEED)]

    def to_dict(self) -> dict:
        return {
            "player_id": self.player_id,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "alive": self.alive,
        }