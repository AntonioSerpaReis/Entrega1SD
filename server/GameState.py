"""
GameState.py — Authoritative server-side game state.

Phase lifecycle:
  LOBBY -> PLAYING -> WAVE_CLEAR -> PLAYING -> ... -> WIN
                   -> GAMEOVER
"""

import time
import random
import threading

from shared.Constants import SCREEN_WIDTH, SCREEN_HEIGHT
from server.dados.Player import Player
from server.dados.Bullet import Bullet
from server.dados.Wave import WaveManager


class GameState:
    def __init__(self):
        self.players: dict[str, Player] = {}
        self.bullets: list[Bullet] = []
        self.wave_mgr = WaveManager()

        self.running = False
        self.phase = "LOBBY"

        self.lock = threading.Lock()

    def add_player(self, player_id: str) -> Player:
        with self.lock:
            spawn_x = SCREEN_WIDTH  / 2 + random.randint(-10, 10)
            spawn_y = SCREEN_HEIGHT / 2 + random.randint(-5, 5)
            p = Player(player_id, spawn_x, spawn_y)
            self.players[player_id] = p
            return p

    def remove_player(self, player_id: str) -> None:
        with self.lock:
            self.players.pop(player_id, None)

    def update(self, dt: float) -> None:
        now = time.time()

        with self.lock:
            if not self.players:
                return
            if self.phase in ("GAMEOVER", "WIN"):
                return

            # Auto-start first wave when players are present
            if self.wave_mgr.state == "WAITING" and self.wave_mgr.wave_number == 0:
                self.wave_mgr.start_next_wave()

            new_bullets = []

            for p in self.players.values():
                if p.alive:
                    new_bullets += p.update(dt, p.latest_input, now)

            self.wave_mgr.update(dt)
            self.bullets += new_bullets

            for b in self.bullets:
                b.update(dt, SCREEN_WIDTH, SCREEN_HEIGHT)

            # Enemy → player collision
            for e in self.wave_mgr.enemies:
                if not e.alive:
                    continue
                for p in self.players.values():
                    if p.alive and int(e.x) == int(p.x) and int(e.y) == int(p.y):
                        p.alive = False

            # Bullet → enemy collision
            for b in self.bullets:
                for e in self.wave_mgr.enemies:
                    if not e.alive:
                        continue
                    if b.overlaps(e.x, e.y):
                        e.take_damage()
                        b.alive = False
                        break

            self.bullets = [b for b in self.bullets if b.alive]

            # Phase transitions
            if self.players and all(not p.alive for p in self.players.values()):
                self.phase = "GAMEOVER"

            elif self.wave_mgr.all_dead():
                self.wave_mgr.mark_clearing()
                if self.wave_mgr.is_final_wave():
                    self.phase = "WIN"
                else:
                    self.wave_mgr.start_next_wave()
                    self.phase = "WAVE_CLEAR"

            elif self.phase == "WAVE_CLEAR":
                self.phase = "PLAYING"

            else:
                self.phase = "PLAYING"

    def to_dict(self) -> dict:
        return {
            "phase":   self.phase,
            "players": {str(pid): p.to_dict() for pid, p in self.players.items()},
            "bullets": [b.to_dict() for b in self.bullets],
            "wave":    self.wave_mgr.to_dict(),
        }