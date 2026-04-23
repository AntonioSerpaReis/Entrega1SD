"""
Renderer.py — Terminal renderer for the game arena.

Symbol legend:
     empty space
  #  player
  ?  enemy
  o  bullet
"""

import os

from shared.Constants import SCREEN_HEIGHT, SCREEN_WIDTH, ENEMY, PLAYER, BULLET, ARENA_SPACE
from client.GameState import ClientGameState


class Renderer:
    def __init__(self, gs: ClientGameState, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):
        self._width  = width
        self._height = height
        self._gs     = gs

    def _clear_screen(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')

    def render(self, enemies: list, bullets: list, players: list) -> None:
        self._clear_screen()

        grid = [[ARENA_SPACE] * self._width for _ in range(self._height)]

        for ex, ey in enemies:
            if 0 <= int(ex) < self._width and 0 <= int(ey) < self._height:
                grid[int(ey)][int(ex)] = ENEMY

        for bx, by in bullets:
            if 0 <= int(bx) < self._width and 0 <= int(by) < self._height:
                grid[int(by)][int(bx)] = BULLET

        for px, py in players:
            if 0 <= int(px) < self._width and 0 <= int(py) < self._height:
                grid[int(py)][int(px)] = PLAYER

        print("\n".join("".join(row) for row in grid))