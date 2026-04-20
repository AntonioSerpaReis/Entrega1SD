"""
Wave.py — Wave manager; spawns enemies and tracks completion.

States:
  WAITING  — between waves (lobby / pregame)
  ACTIVE   — enemies alive
  CLEARING — wave just ended, waiting for next wave trigger
"""

import random

from shared.Constants import ENEMIES_PER_WAVE_BASE, ENEMIES_PER_WAVE_SCALE, SCREEN_WIDTH, SCREEN_HEIGHT
from server.dados.Enemy import Enemy


class WaveManager:
    TOTAL_WAVES = 10

    def __init__(self):
        self.wave_number = 0
        self.enemies: list[Enemy] = []
        self.state = "WAITING"

    def start_next_wave(self) -> None:
        self.wave_number += 1
        count = ENEMIES_PER_WAVE_BASE + (self.wave_number - 1) * ENEMIES_PER_WAVE_SCALE
        self.enemies = self._spawn_enemies(count)
        self.state = "ACTIVE"

    def update(self, dt: float) -> None:
        if self.state != "ACTIVE":
            return
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update(dt)

    def all_dead(self) -> bool:
        if self.state != "ACTIVE":
            return False
        return all(not e.alive for e in self.enemies)

    def is_final_wave(self) -> bool:
        return self.wave_number >= self.TOTAL_WAVES

    def mark_clearing(self) -> None:
        self.state = "CLEARING"

    def mark_waiting(self) -> None:
        self.state = "WAITING"

    def living_enemies(self) -> list[Enemy]:
        return [e for e in self.enemies if e.alive]

    def _spawn_enemies(self, count: int) -> list[Enemy]:
        """Spawn enemies along the arena border, away from the centre."""
        enemies = []
        margin = 3
        sides = ["top", "bottom", "left", "right"]

        for _ in range(count):
            side = random.choice(sides)
            if side == "top":
                x, y = random.randint(margin, SCREEN_WIDTH - margin), margin
            elif side == "bottom":
                x, y = random.randint(margin, SCREEN_WIDTH - margin), SCREEN_HEIGHT - margin
            elif side == "left":
                x, y = margin, random.randint(margin, SCREEN_HEIGHT - margin)
            elif side == "right": 
                x, y = SCREEN_WIDTH - margin, random.randint(margin, SCREEN_HEIGHT - margin)
            enemies.append(Enemy(x, y, self.wave_number))

        return enemies

    def to_dict(self) -> dict:
        return {
            "wave_number": self.wave_number,
            "state": self.state,
            "enemies": [e.to_dict() for e in self.enemies if e.alive],
        }