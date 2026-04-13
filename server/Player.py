"""
Player.py — Server-side player model.
"""

import math # usado para cálculos trigonométricos na direção das balas e na movimentação dos jogadores
import time # usado para controlar o tempo de recarga das habilidades, duração da loja e tempo entre as ondas

from shared.Constants import (
    BASE_HP, BASE_MANA, BASE_SPEED, DASH_SPEED, DASH_DURATION, DASH_COOLDOWN,
    BULLET_SPEED, PLAYER_BULLET_DAMAGE, PLAYER_RADIUS,
    UPGRADE_DAMAGE_COST, UPGRADE_HP_COST, UPGRADE_MANA_COST,
    UPGRADE_DAMAGE_AMOUNT, UPGRADE_HP_AMOUNT, UPGRADE_MANA_AMOUNT,
    SCREEN_WIDTH, SCREEN_HEIGHT,
) # usado para definir as características dos jogadores, os custos e benefícios das melhorias e para limitar seu movimento dentro da arena
from shared.Classes import get_class # usado para obter as definições de classe dos jogadores, como cor e efeito de habilidade
from server.Bullet import Bullet # usado para criar as balas disparadas pelos jogadores


class Player:
    """
    Authoritative server-side player state.
    All physics units are pixels/second.
    """

    FIRE_RATE = 0.18          # seconds between shots
    MANA_REGEN = 4.0          # mana per second

    def __init__(self, player_id: int, class_id: int, spawn_x: float, spawn_y: float):
        self.player_id = player_id
        self.class_id = class_id
        self.class_def = get_class(class_id)

        # Position / movement
        self.x = spawn_x
        self.y = spawn_y
        self.radius = PLAYER_RADIUS

        # Stats (base + upgrades)
        self.max_hp = BASE_HP
        self.hp = BASE_HP
        self.max_mana = BASE_MANA
        self.mana = float(BASE_MANA)
        self.speed = BASE_SPEED
        self.damage = PLAYER_BULLET_DAMAGE

        # Economy
        self.coins = 0

        # Upgrade levels
        self.upgrades = {"damage": 0, "hp": 0, "mana": 0}

        # State flags
        self.alive = True
        self.invulnerable = False
        self.invulnerable_until = 0.0

        # Dash
        self.dash_active = False
        self.dash_vx = 0.0
        self.dash_vy = 0.0
        self.dash_end_time = 0.0
        self.dash_cd_end = 0.0

        # Ability
        self.ability_cd_end = 0.0
        self.ability_active = False          # currently executing timed ability
        self.ability_end_time = 0.0
        # Berserker charge state
        self.charge_vx = 0.0
        self.charge_vy = 0.0

        # Shooting
        self.fire_cd_end = 0.0

        # Mouse aim (world coords sent by client)
        self.aim_x = spawn_x
        self.aim_y = spawn_y

    # ── Helpers ───────────────────────────────────────────────────────────────

    @property
    def color(self):
        return self.class_def["color"]

    def is_invulnerable(self) -> bool:
        """Returns True if the player is currently invulnerable (just after taking damage)."""
        return self.invulnerable and time.time() < self.invulnerable_until

    # ── Per-tick update ───────────────────────────────────────────────────────

    def update(self, dt: float, keys: dict, mouse: dict, shoot: bool, now: float) -> list[Bullet]:
        """Update player state based on input and timers. Returns a list of bullets spawned this tick."""
        if not self.alive:
            return []

        self.aim_x = mouse.get("x", self.aim_x)
        self.aim_y = mouse.get("y", self.aim_y)

        # Mana regeneration
        self.mana = min(self.max_mana, self.mana + self.MANA_REGEN * dt)

        # Invulnerability timeout
        if self.invulnerable and now >= self.invulnerable_until:
            self.invulnerable = False

        # Ability timed end
        if self.ability_active and now >= self.ability_end_time:
            self.ability_active = False

        self._move(dt, keys, now)
        bullets = self._shoot(shoot, now)
        return bullets

    def _move(self, dt: float, keys: dict, now: float) -> None:
        """Update player position based on input and dash/ability state."""
        # Berserker charge overrides movement
        if self.ability_active and self.class_def["ability_effect"] == "charge":
            self.x += self.charge_vx * dt
            self.y += self.charge_vy * dt
            self._clamp()
            return

        # Normal dash
        if self.dash_active:
            if now >= self.dash_end_time:
                self.dash_active = False
            else:
                self.x += self.dash_vx * dt
                self.y += self.dash_vy * dt
                self._clamp()
                return

        # WASD / arrow movement
        dx, dy = 0.0, 0.0
        if keys.get("up"): dy -= 1
        if keys.get("down"): dy += 1
        if keys.get("left"): dx -= 1
        if keys.get("right"): dx += 1

        if dx != 0 or dy != 0:
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length

        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt
        self._clamp()

        # Initiate dash
        if keys.get("dash") and now >= self.dash_cd_end:
            if dx != 0 or dy != 0:
                self.dash_vx = dx * DASH_SPEED
                self.dash_vy = dy * DASH_SPEED
            else:
                # dash toward mouse if standing still
                adx = self.aim_x - self.x
                ady = self.aim_y - self.y
                dist = math.sqrt(adx*adx + ady*ady) or 1
                self.dash_vx = (adx / dist) * DASH_SPEED
                self.dash_vy = (ady / dist) * DASH_SPEED
            self.dash_active = True
            self.dash_end_time = now + DASH_DURATION
            self.dash_cd_end = now + DASH_COOLDOWN

    def _clamp(self):
        """Keep the player within arena bounds."""
        self.x = max(self.radius, min(SCREEN_WIDTH  - self.radius, self.x))
        self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y))

    def _shoot(self, shoot: bool, now: float) -> list[Bullet]:
        """Return a list of bullets spawned by shooting this tick."""
        if not shoot or now < self.fire_cd_end:
            return []
        self.fire_cd_end = now + self.FIRE_RATE

        dx = self.aim_x - self.x
        dy = self.aim_y - self.y
        dist = math.sqrt(dx*dx + dy*dy) or 1
        vx = (dx / dist) * BULLET_SPEED
        vy = (dy / dist) * BULLET_SPEED

        return [Bullet(self.x, self.y, vx, vy, self.damage, "player", self.player_id)]

    # ── Damage / healing ─────────────────────────────────────────────────────

    INVINCIBILTY_FRAMES_DURATION = 0.6   # seconds of invulnerability granted after a hit

    def take_damage(self, amount: int) -> None:
        """Apply damage to the player, triggering invulnerability frames. If HP drops to 0, mark as dead."""
        if not self.alive or self.is_invulnerable():
            return
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.alive = False
        else:
            self.invulnerable = True
            self.invulnerable_until = time.time() + self.INVINCIBILTY_FRAMES_DURATION

    def heal(self, amount: int) -> None:
        """Heal the player by the given amount, without exceeding max HP."""
        self.hp = min(self.max_hp, self.hp + amount)

    # ── Shop upgrades ─────────────────────────────────────────────────────────

    def buy_upgrade(self, upgrade: str) -> bool:
        """Attempt to purchase an upgrade. If successful, apply its effects and return True. Otherwise return False."""
        costs = {"damage": UPGRADE_DAMAGE_COST,
                 "hp": UPGRADE_HP_COST,
                 "mana": UPGRADE_MANA_COST}
        cost = costs.get(upgrade, 9999)
        if self.coins < cost:
            return False
        self.coins -= cost
        self.upgrades[upgrade] = self.upgrades.get(upgrade, 0) + 1
        if upgrade == "damage":
            self.damage += UPGRADE_DAMAGE_AMOUNT
        elif upgrade == "hp":
            self.max_hp += UPGRADE_HP_AMOUNT
            self.hp = min(self.hp + UPGRADE_HP_AMOUNT, self.max_hp)
        elif upgrade == "mana":
            self.max_mana += UPGRADE_MANA_AMOUNT
        return True

    # ── Serialization ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Convert the player to a dictionary for sending to clients."""
        now = time.time()
        return {
            "player_id":      self.player_id,
            "class_id":       self.class_id,
            "color":          list(self.color),
            "x":              round(self.x, 1),
            "y":              round(self.y, 1),
            "hp":             self.hp,
            "max_hp":         self.max_hp,
            "mana":           round(self.mana, 1),
            "max_mana":       self.max_mana,
            "coins":          self.coins,
            "damage":         self.damage,
            "alive":          self.alive,
            "invulnerable":   self.is_invulnerable(),
            "dash_active":    self.dash_active,
            "ability_cd":     max(0.0, round(self.ability_cd_end - now, 2)),
            "upgrades":       self.upgrades,
        }