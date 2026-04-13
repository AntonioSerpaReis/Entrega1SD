"""
InputHandler.py — Captures keyboard and mouse state each frame.

Produces a dict compatible with Protocol.make_input().
"""

import pygame # usado para tipos de eventos, constantes de teclas e operações de desenho
from shared.Protocol import make_input # usado para construir a mensagem de input a ser enviada ao servidor


class InputHandler:
    """
    Polls pygame events and keyboard state once per frame.
    Call update() at the top of each frame before reading properties.
    """

    def __init__(self):
        self._keys = {}
        self._mouse_x = 0.0
        self._mouse_y = 0.0
        self._mouse_btn = False
        self._ability = False
        self._quit = False

        # Camera offset supplied by Renderer each frame
        self.cam_x = 0
        self.cam_y = 0

    # ── Frame update ──────────────────────────────────────────────────────────

    def update(self, events: list) -> None:
        """Call once per frame with the frame's event list."""
        self._ability = False

        for event in events:
            if event.type == pygame.QUIT:
                self._quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._ability = True
                if event.key == pygame.K_ESCAPE:
                    self._quit = True

        kb = pygame.key.get_pressed()
        self._keys = {
            "up": kb[pygame.K_w],
            "down": kb[pygame.K_s],
            "left": kb[pygame.K_a],
            "right": kb[pygame.K_d],
            "dash": kb[pygame.K_LSHIFT],
        }

        # Mouse world coords = screen pos + camera offset
        sx, sy = pygame.mouse.get_pos()
        self._mouse_x = sx + self.cam_x
        self._mouse_y = sy + self.cam_y
        btns = pygame.mouse.get_pressed()
        self._mouse_btn = bool(btns[0])

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def quit(self) -> bool:
        return self._quit

    @property
    def ability_pressed(self) -> bool:
        return self._ability

    @property
    def shooting(self) -> bool:
        return self._mouse_btn

    @property
    def mouse_world(self) -> tuple[float, float]:
        return (self._mouse_x, self._mouse_y)

    @property
    def mouse_screen(self) -> tuple[int, int]:
        return pygame.mouse.get_pos()

    # ── Build protocol message ────────────────────────────────────────────────

    def build_input_msg(self) -> dict:
        mx, my = self._mouse_x, self._mouse_y
        return make_input(
            keys = self._keys,
            mouse_x = mx,
            mouse_y = my,
            mouse_btn = self._mouse_btn,
            ability = self._ability,
        )