"""
Bullet.py — Server-side bullet model.
"""

import uuid # usado para gerar IDs únicos para as balas


class Bullet:
    """
    Represents a single bullet travelling in a fixed direction.

    owner:   "player"  or  "enemy"
    owner_id: player_id (int) or enemy_id (str)
    """

    def __init__(self, x: float, y: float, vx: float, vy: float, damage: int, owner: str, owner_id, radius: int = 6, lifetime: float = 4.0):
        self.id = str(uuid.uuid4())[:8]
        self.x = x                # pixels from top-left corner horizontally
        self.y = y                # pixels from top-left corner vertically
        self.vx = vx              # pixels per second horizontally
        self.vy = vy              # pixels per second vertically
        self.damage = damage      # damage dealt to player / enemy on hit
        self.owner = owner        # "player" | "enemy"
        self.owner_id = owner_id  # player_id (int) or enemy_id (str)
        self.radius = radius      # for collision detection
        self.lifetime = lifetime  # seconds until auto-removal
        self.alive = True         # set to False on collision or when lifetime expires

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, tempo: float, arena_w: int, arena_h: int) -> None:
        """Move the bullet forward by tempo seconds. Despawn if it goes out of bounds or exceeds lifetime."""
        if not self.alive:
            return
        self.x += self.vx * tempo
        self.y += self.vy * tempo
        self.lifetime -= tempo

        if self.lifetime <= 0:
            self.alive = False
            return
        
        # out-of-arena removal
        margin = self.radius
        if (self.x < -margin or self.x > arena_w + margin or self.y < -margin or self.y > arena_h + margin):
            self.despawn()

    def despawn(self):
        """Mark the bullet as dead so it will be removed from the game state."""
        self.alive = False

    # ── Collision helper ──────────────────────────────────────────────────────

    def overlaps(self, circlex: float, circley: float, circle_radius: float) -> bool:
        """Check if this bullet overlaps with a circle at (circlex, circley) with radius circle_radius."""
        dx = self.x - circlex
        dy = self.y - circley
        dist = self.radius + circle_radius
        return (dx * dx + dy * dy) < (dist * dist)

    # ── Serialization ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Convert the bullet to a dictionary for sending to clients."""
        return {
            "id": self.id,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "vx": round(self.vx, 1),
            "vy": round(self.vy, 1),
            "owner": self.owner,
            "radius": self.radius,
            "damage": self.damage,
        }