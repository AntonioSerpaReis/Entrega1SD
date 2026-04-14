"""
GameState.py — Authoritative server game state.

Coordinates:
  • Player input is applied
  • Bullet positions are advanced
  • Collisions are resolved
  • Wave progression is managed
  • Ability effects are applied
"""

import math # usado para cálculos trigonométricos na direção das balas e na movimentação dos inimigos
import time # usado para controlar o tempo de recarga das habilidades, duração da loja e tempo entre as ondas
import random # usado para spawnar inimigos em posições aleatórias e para variar o tempo de disparo e o ângulo inicial do padrão de tiro

from shared.Constants import SCREEN_WIDTH, SCREEN_HEIGHT, ENEMY_COIN_REWARD # usado para definir os limites da arena e a recompensa em moedas por matar inimigos
from server.Player import Player # usado para criar e atualizar os jogadores
from server.Bullet import Bullet # usado para criar e atualizar as balas
from server.Wave   import WaveManager # usado para gerenciar as ondas de inimigos, incluindo spawn

class Event:
    def __init__(self, name: str):
        self.name = name
        self.handler = None

    def connect(self, func):
        """Connect a handler function to this event."""
        print(f"[EVENTO] Server: {self.name}")
        self.handler = func

    def emit(self, data=None):
        """Call the handler function with optional data."""
        if self.handler:
            if data is not None:
                self.handler(data)  # Aqui o 'n' é passado explicitamente
            else:
                self.handler()      # Para eventos sem dados (ex: Game Over)

class GameState:
    """
    Central game state updated once per server tick.
    Holds players, bullets, and the wave manager.
    """

    SHOP_DURATION = 10.0    # seconds the shop stays open

    def __init__(self):
        self.players:  dict[int, Player] = {}
        self.bullets:  list[Bullet]      = []
        self.wave_mgr: WaveManager       = WaveManager()

        self.running       = False
        self.phase         = "LOBBY"      # LOBBY | SHOP | WAVE | GAMEOVER | WIN
        self.shop_end_time = 0.0

        # callback set by Server
        self.on_wave_start = Event("Wave Start")
        self.on_wave_clear = Event("Wave Clear")
        self.on_shop_open  = Event("Shop Open")
        self.on_shop_close = Event("Shop Close")
        self.on_game_over  = Event("Game Over")
        self.on_game_win   = Event("Game Win")

    # ── Player management ─────────────────────────────────────────────────────

    def add_player(self, player_id: int, class_id: int = 0) -> Player:
        spawn_x = SCREEN_WIDTH  / 2 + random.randint(-120, 120)
        spawn_y = SCREEN_HEIGHT / 2 + random.randint(-120, 120)
        p = Player(player_id, class_id, spawn_x, spawn_y)
        self.players[player_id] = p
        return p

    def remove_player(self, player_id: int) -> None:
        self.players.pop(player_id, None)

    # ── Main tick ─────────────────────────────────────────────────────────────

    def update(self, dt: float, inputs: dict) -> None:
        """
        inputs: {player_id: {"keys": {...}, "mouse": {...},
                              "shoot": bool, "ability": bool}}
        """
        now = time.time()

        if self.phase == "LOBBY":
            if len(self.players) > 0:
                self._start_game()
            return

        if self.phase == "SHOP":
            if now >= self.shop_end_time:
                self._close_shop()
            # Players can still move in shop
            for pid, inp in inputs.items():
                p = self.players.get(pid)
                if p and p.alive:
                    p.update(dt, inp["keys"], inp["mouse"], False, now)
            return

        if self.phase in ("GAMEOVER", "WIN"):
            return

        # ── WAVE phase ──────────────────────────────────────────────────────
        new_bullets = []

        # Update players
        for pid, inp in inputs.items():
            p = self.players.get(pid)
            if p and p.alive:
                # Ability request
                if inp.get("ability"):
                    ab = self._apply_ability(p, now)
                    new_bullets += ab

                pb = p.update(dt, inp["keys"], inp["mouse"], inp.get("shoot", False), now)
                new_bullets += pb

        # Update enemies via wave manager
        living_players = list(self.players.values())
        new_bullets += self.wave_mgr.update(dt, living_players, now)

        self.bullets += new_bullets

        # Advance all bullets
        for b in self.bullets:
            b.update(dt, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Collision: enemy bullets → players
        for b in self.bullets:
            if b.owner != "enemy" or not b.alive:
                continue
            for p in self.players.values():
                if not p.alive:
                    continue
                if b.overlaps(p.x, p.y, p.radius):
                    p.take_damage(b.damage)
                    b.alive = False
                    break

        # Collision: player bullets → enemies
        for b in self.bullets:
            if b.owner != "player" or not b.alive:
                continue
            for e in self.wave_mgr.enemies:
                if not e.alive:
                    continue
                if b.overlaps(e.x, e.y, e.radius):
                    e.take_damage(b.damage)
                    b.alive = False
                    if not e.alive:
                        # reward coins to shooter
                        shooter = self.players.get(b.owner_id)
                        if shooter:
                            shooter.coins += ENEMY_COIN_REWARD
                    break

        # Berserker charge collision
        for p in self.players.values():
            if not p.alive or not p.ability_active:
                continue
            if p.class_def["ability_effect"] != "charge":
                continue
            for e in self.wave_mgr.enemies:
                if not e.alive:
                    continue
                dx = e.x - p.x
                dy = e.y - p.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < p.radius + e.radius:
                    dmg = p.class_def["ability_params"]["damage"]
                    e.take_damage(dmg)
                    if not e.alive:
                        p.coins += ENEMY_COIN_REWARD

        # Remove dead bullets
        bullets = []
        for b in self.bullets:
            if b.alive:
                bullets.append(b)
        self.bullets = bullets

        # Check wave clear
        if self.wave_mgr.all_dead():
            self.wave_mgr.mark_clearing()
            self._on_wave_cleared()

        # Check game over (all players dead)
        if all(not p.alive for p in self.players.values()):
            self.phase = "GAMEOVER"
            if self.on_game_over:
                self.on_game_over.emit()

    # ── Abilities ─────────────────────────────────────────────────────────────

    def _apply_ability(self, player: Player, now: float) -> list[Bullet]:
        cd_end = player.ability_cd_end
        cd = player.class_def["ability_cd"]
        cost = player.class_def["mana_cost"]
        effect = player.class_def["ability_effect"]
        params = player.class_def["ability_params"]

        if now < cd_end or player.mana < cost:
            return []

        player.mana -= cost
        player.ability_cd_end = now + cd
        new_bullets = []

        if effect == "radial_burst":
            count = params["count"]
            speed = params["speed"]
            dmg = int(player.damage * params["damage_mult"])
            step = 360.0 / count
            for i in range(count):
                rad = math.radians(i * step)
                vx = math.cos(rad) * speed
                vy = math.sin(rad) * speed
                new_bullets.append(
                    Bullet(player.x, player.y, vx, vy,
                           dmg, "player", player.player_id))

        elif effect == "invulnerable":
            player.invulnerable       = True
            player.invulnerable_until = now + params["duration"]

        elif effect == "nova":
            radius = params["radius"]
            damage = params["damage"]
            # destroy bullets near player
            for b in self.bullets:
                if b.owner == "enemy":
                    dx = b.x - player.x
                    dy = b.y - player.y
                    if math.sqrt(dx*dx + dy*dy) < radius:
                        b.alive = False
            # damage enemies
            for e in self.wave_mgr.enemies:
                if not e.alive:
                    continue
                dx = e.x - player.x
                dy = e.y - player.y
                if math.sqrt(dx*dx + dy*dy) < radius:
                    e.take_damage(damage)
                    if not e.alive:
                        player.coins += ENEMY_COIN_REWARD

        elif effect == "teleport":
            max_range = params["max_range"]
            dx = player.aim_x - player.x
            dy = player.aim_y - player.y
            dist = math.sqrt(dx*dx + dy*dy) or 1
            dist = min(dist, max_range)
            player.x = max(player.radius, min(SCREEN_WIDTH  - player.radius, player.x + (dx / dist) * dist))
            player.y = max(player.radius, min(SCREEN_HEIGHT - player.radius, player.y + (dy / dist) * dist))

        elif effect == "heal_aura":
            radius = params["radius"]
            heal = params["heal"]
            for p in self.players.values():
                if not p.alive:
                    continue
                dx = p.x - player.x
                dy = p.y - player.y
                if math.sqrt(dx*dx + dy*dy) < radius:
                    p.heal(heal)

        elif effect == "slow_enemies":
            for e in self.wave_mgr.enemies:
                e.apply_slow(params["slow_factor"], params["duration"], now)

        elif effect == "charge":
            dx = player.aim_x - player.x
            dy = player.aim_y - player.y
            dist = math.sqrt(dx*dx + dy*dy) or 1
            speed = params["speed"]
            player.charge_vx = (dx / dist) * speed
            player.charge_vy = (dy / dist) * speed
            player.ability_active = True
            player.ability_end_time = now + params["duration"]

        return new_bullets

    # ── Phase transitions ─────────────────────────────────────────────────────

    def _start_game(self) -> None:
        self.running = True
        self._open_shop_first_time()

    def _open_shop_first_time(self) -> None:
        self.phase = "SHOP"
        self.shop_end_time = time.time() + self.SHOP_DURATION
        self.on_shop_open.emit()

    def _close_shop(self) -> None:
        self.phase = "WAVE"
        for p in self.players.values():
            if not p.alive:
                p.alive = True
                p.hp = max(1, p.max_hp // 2)
        
        self.wave_mgr.start_next_wave()
        
        self.on_wave_start.emit(self.wave_mgr.wave_number)
        self.on_shop_close.emit()

    def _on_wave_cleared(self) -> None:
        self.on_wave_clear.emit(self.wave_mgr.wave_number)
        
        if self.wave_mgr.is_final_wave():
            self.phase = "WIN"
            self.on_game_win.emit()
        else:
            self.phase = "SHOP"
            self.shop_end_time = time.time() + self.SHOP_DURATION
            self.on_shop_open.emit()

    # ── Serialization ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "phase": self.phase,
            "players": {str(pid): p.to_dict() for pid, p in self.players.items()},
            "wave": self.wave_mgr.to_dict(),
            "shop_remaining": max(0.0, round(self.shop_end_time - time.time(), 1)) if self.phase == "SHOP" else 0.0,
        }