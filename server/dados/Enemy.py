"""
Enemy.py — Server-side enemy model.
"""

from uuid import uuid4
from random import randint

from server import ENEMY_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT


class Enemy:
    def __init__(self, x: float, y: float, wave: int):
        self.id: str    = str(uuid4())[:8]
        self.x: int     = x
        self.y: int     = y
        self.radius: int = 1        # for collision purposes
        self.alive: bool = True
        self.target_x: int = randint(0, SCREEN_WIDTH  - 1)
        self.target_y: int = randint(0, SCREEN_HEIGHT - 1)
        self.speed: int = ENEMY_SPEED + wave  # scales with wave number

    def update(self, dt: float) -> None:
        if not self.alive:
            return
        self._move_randomly(dt)
        self._clamp()

    def _move_randomly(self, dt: float) -> None:
        dx: int = self.target_x - self.x
        dy: int = self.target_y - self.y
        if abs(dx) < 0.2 and abs(dy) < 0.2:
            self.target_x = randint(0, SCREEN_WIDTH  - 1)
            self.target_y = randint(0, SCREEN_HEIGHT - 1)
            return
        if abs(dx) > 0.1:
            self.x += int((1 if dx > 0 else -1) * self.speed * dt)
        elif abs(dy) > 0.1:
            self.y += int((1 if dy > 0 else -1) * self.speed * dt)

    def _clamp(self) -> None:
        self.x = max(0, min(SCREEN_WIDTH  - 1, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - 1, self.y))

    def take_damage(self) -> None:
        self.alive = False

    def overlaps(self, target_x: int, target_y: int) -> bool:
        return abs(self.x - target_x) <= self.radius and abs(self.y - target_y) <= self.radius

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "alive": self.alive,
        }