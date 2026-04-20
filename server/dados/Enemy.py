"""
Enemy.py — Server-side enemy model.

Behaviour: wanders randomly toward successive random targets; dies in one hit.
"""

import uuid
import random

from shared.Constants import ENEMY_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT


class Enemy:
    def __init__(self, x: float, y: float, wave: int):
        self.id    = str(uuid.uuid4())[:8]
        self.x     = x
        self.y     = y
        self.alive = True

        self.target_x = random.randint(0, SCREEN_WIDTH  - 1)
        self.target_y = random.randint(0, SCREEN_HEIGHT - 1)

        self.speed = ENEMY_SPEED + wave  # scales with wave number

    def update(self, dt: float) -> None:
        if not self.alive:
            return
        self._move_randomly(dt)
        self._clamp()

    def _move_randomly(self, dt: float) -> None:
        dx = self.target_x - self.x
        dy = self.target_y - self.y

        if abs(dx) < 0.2 and abs(dy) < 0.2:
            # Reached target — pick a new one
            self.target_x = random.randint(0, SCREEN_WIDTH  - 1)
            self.target_y = random.randint(0, SCREEN_HEIGHT - 1)
            return

        if abs(dx) > 0.1:
            self.x += (1 if dx > 0 else -1) * self.speed * dt
        elif abs(dy) > 0.1:
            self.y += (1 if dy > 0 else -1) * self.speed * dt

    def _clamp(self) -> None:
        self.x = max(0, min(SCREEN_WIDTH  - 1, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - 1, self.y))

    def take_damage(self) -> None:
        self.alive = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "alive": self.alive,
        }