"""
Enemy.py — Server-side enemy with bullet patterns.

One enemy type: a rotating multi-shot "spinner" that fires in
N directions simultaneously, with the pattern slowly rotating
each cycle to create a spiralling wall effect.
"""

import math # usado para cálculos trigonométricos na direção das balas e na movimentação dos inimigos
import uuid # usado para gerar IDs únicos para os inimigos
import random # usado para spawnar inimigos em posições aleatórias e para variar o tempo de disparo e o ângulo inicial do padrão de tiro

from shared.Constants import (
    ENEMY_RADIUS, ENEMY_SPEED, ENEMY_BULLET_SPEED,
    ENEMY_BULLET_DAMAGE, SCREEN_WIDTH, SCREEN_HEIGHT
) # usado para definir as características dos inimigos e para limitar seu movimento dentro da arena
from server.Bullet import Bullet # usado para criar as balas disparadas pelos inimigos


class Enemy:
    # Fire-pattern parameters
    SHOT_COUNT = 6       # bullets per burst
    FIRE_INTERVAL = 1.8     # seconds between bursts
    ROTATION_STEP = 15.0    # degrees added to pattern angle each burst
    SLOW_FACTOR = 1.0     # multiplied when slowed (set to <1 externally)

    def __init__(self, x: float, y: float, hp: int, wave: int):
        self.id = str(uuid.uuid4())[:8]
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.radius = ENEMY_RADIUS
        self.alive = True

        # Scale stats with wave
        self.speed = ENEMY_SPEED + wave * 3
        self.bullet_dmg = ENEMY_BULLET_DAMAGE + wave
        self.bullet_spd = ENEMY_BULLET_SPEED + wave * 4

        # Pattern rotation (accumulates over time)
        self._pattern_angle = random.uniform(0, 360)
        self._fire_timer = random.uniform(0, self.FIRE_INTERVAL)  # stagger

        # Random wander target
        self._target_x = random.randint(100, SCREEN_WIDTH  - 100)
        self._target_y = random.randint(100, SCREEN_HEIGHT - 100)
        self._wander_timer = 0.0

        # Slow state — set by apply_slow(), read in _move()
        self.slow_factor = 1.0
        self.slow_until = 0.0

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, tempo: float, players: list, now: float) -> list[Bullet]:
        if not self.alive:
            return []

        self._move(tempo, players, now)
        bullets = self._fire_pattern(tempo)
        return bullets

    def _move(self, tempo: float, players: list, now: float) -> None:
        target = self._nearest_player(players)
        if target:
            tx, ty = target.x, target.y
        else:
            self._wander_timer -= tempo
            if self._wander_timer <= 0:
                self._target_x = random.randint(100, SCREEN_WIDTH  - 100)
                self._target_y = random.randint(100, SCREEN_HEIGHT - 100)
                self._wander_timer = random.uniform(2.0, 4.0)
            tx, ty = self._target_x, self._target_y

        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        effective_slow = self.slow_factor if now < self.slow_until else 1.0
        spd  = self.speed * effective_slow
        if dist > self.radius + 10:
            self.x += (dx / dist) * spd * tempo
            self.y += (dy / dist) * spd * tempo
        # clamp
        self.x = max(self.radius, min(SCREEN_WIDTH  - self.radius, self.x))
        self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y))

    def _nearest_player(self, players: list):
        living = [p for p in players if p.alive]
        
        if not living:
            return None

        nearest = living[0]
        min_dist_sq = (nearest.x - self.x)**2 + (nearest.y - self.y)**2

        for i in range(1, len(living)):
            p = living[i]
            dist_sq = (p.x - self.x)**2 + (p.y - self.y)**2
            
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest = p
        
        return nearest

    def _fire_pattern(self, tempo: float) -> list[Bullet]:
        self._fire_timer += tempo
        if self._fire_timer < self.FIRE_INTERVAL:
            return []
        self._fire_timer = 0.0

        bullets = []
        step = 360.0 / self.SHOT_COUNT
        for i in range(self.SHOT_COUNT):
            angle_deg = self._pattern_angle + i * step
            angle_rad = math.radians(angle_deg)
            vx = math.cos(angle_rad) * self.bullet_spd
            vy = math.sin(angle_rad) * self.bullet_spd
            bullets.append(Bullet(self.x, self.y, vx, vy, self.bullet_dmg, "enemy", self.id, radius=7))
        self._pattern_angle = (self._pattern_angle + self.ROTATION_STEP) % 360
        return bullets

    # ── Damage ────────────────────────────────────────────────────────────────

    def take_damage(self, amount: int) -> None:
        """Apply damage to the enemy. If HP drops to 0, mark as dead."""
        if not self.alive:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def apply_slow(self, slow_factor: float, duration: float, now: float):
        """Apply a slowing effect to the enemy, reducing its speed by `slow_factor` for `duration` seconds."""
        self.slow_factor = slow_factor
        self.slow_until  = now + duration

    # ── Serialization ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Convert the enemy to a dictionary for sending to clients."""
        return {
            "id": self.id,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "hp": self.hp,
            "max_hp": self.max_hp,
            "alive": self.alive,
            "radius": self.radius,
        }