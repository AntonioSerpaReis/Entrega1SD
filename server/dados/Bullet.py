"""
Bullet.py — Server-side bullet model.
"""

from uuid import uuid4
from server import BULLET_LIFETIME

class Bullet:
    """A single bullet travelling in a fixed direction."""

    def __init__(self, x: float, y: float, vx: float, vy: float, lifetime: float = BULLET_LIFETIME) -> None:
        self.id: str = str(uuid4())[:8]
        self.x: int = x
        self.y: int = y
        self.vx: int = vx        # horizontal velocity (units/second)
        self.vy: int = vy        # vertical velocity   (units/second)
        self.radius: int = 1        # for collision purposes
        self.lifetime: float = lifetime  # seconds until auto-removal
        self.alive: bool = True

    def update(self, dt: float, arena_w: int, arena_h: int) -> None:
        """Advance position; despawn on lifetime expiry or out-of-bounds."""
        if not self.alive:
            return

        self.x += int(self.vx * dt)
        self.y += int(self.vy * dt)
        self.lifetime -= dt

        if self.lifetime <= 0:
            self.alive = False
            return

        if self.x < 0 or self.x >= arena_w or self.y < 0 or self.y >= arena_h:
            self.alive = False

    def despawn(self) -> None:
        self.alive = False

    def overlaps(self, target_x: int, target_y: int) -> bool:
        return abs(self.x - target_x) <= self.radius and abs(self.y - target_y) <= self.radius

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
        }