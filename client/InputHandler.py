"""
InputHandler.py — Pygame keyboard event listener.

WASD  → movement
Arrows → shooting direction
"""

import pygame
from client import MSG_INPUT


class InputHandler:
    def __init__(self):
        self._keys = {
            "up": False, "down": False, "left": False, "right": False,
            "attack_up": False, "attack_down": False,
            "attack_left": False, "attack_right": False,
        }
        self._quit = False

    @property
    def quit(self) -> bool:
        return self._quit

    def handle_events(self) -> None:
        """Processes Pygame events. Call this inside your main game loop."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit = True
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:     self._quit = True
                elif event.key == pygame.K_w:        self._keys["up"] = True
                elif event.key == pygame.K_s:        self._keys["down"] = True
                elif event.key == pygame.K_a:        self._keys["left"] = True
                elif event.key == pygame.K_d:        self._keys["right"] = True
                elif event.key == pygame.K_UP:       self._keys["attack_up"] = True
                elif event.key == pygame.K_DOWN:     self._keys["attack_down"] = True
                elif event.key == pygame.K_LEFT:     self._keys["attack_left"] = True
                elif event.key == pygame.K_RIGHT:    self._keys["attack_right"] = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:          self._keys["up"] = False
                elif event.key == pygame.K_s:        self._keys["down"] = False
                elif event.key == pygame.K_a:        self._keys["left"] = False
                elif event.key == pygame.K_d:        self._keys["right"] = False
                elif event.key == pygame.K_UP:       self._keys["attack_up"] = False
                elif event.key == pygame.K_DOWN:     self._keys["attack_down"] = False
                elif event.key == pygame.K_LEFT:     self._keys["attack_left"] = False
                elif event.key == pygame.K_RIGHT:    self._keys["attack_right"] = False

    def build_input_msg(self) -> dict:
        return {"type": MSG_INPUT, "keys": dict(self._keys)}