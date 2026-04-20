"""
Bullet.py — Server-side bullet model.
"""

import uuid


class Bullet:
    """A single bullet travelling in a fixed direction."""

    def __init__(self, x: float, y: float, vx: float, vy: float, lifetime: float = 4.0):
        self.id = str(uuid.uuid4())[:8]
        self.x = x
        self.y = y
        self.vx = vx        # horizontal velocity (units/second)
        self.vy = vy        # vertical velocity   (units/second)
        self.lifetime = lifetime  # seconds until auto-removal
        self.alive = True

    def update(self, dt: float, arena_w: int, arena_h: int) -> None:
        """Advance position; despawn on lifetime expiry or out-of-bounds."""
        if not self.alive:
            return

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt

        if self.lifetime <= 0:
            self.alive = False
            return

        if self.x < 0 or self.x >= arena_w or self.y < 0 or self.y >= arena_h:
            self.alive = False

    def despawn(self) -> None:
        self.alive = False

    def overlaps(self, target_x: float, target_y: float) -> bool:
        return int(self.x) == int(target_x) and int(self.y) == int(target_y)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
        }