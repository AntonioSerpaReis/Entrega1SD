import sys
import pygame
from random import choice
from client.assets.arena_colors import ARENA_BG
from client import SCREEN_HEIGHT, SCREEN_WIDTH
from client.GameState import ClientGameState

classes = ["client/assets/aisha.png",
           "client/assets/bloom.png",
           "client/assets/stella.png",
           "client/assets/flora.png",
           "client/assets/musa.png",
           "client/assets/tecna.png",]

class Renderer:
    def __init__(self, gs: ClientGameState, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):
        pygame.init()
        self._width = width
        self._height = height
        self._gs = gs
        self.scale = 20
        self.screen = pygame.display.set_mode((self._width * self.scale, self._height * self.scale))
        pygame.display.set_caption("Multiplayer Arena")

        try:
            self._player_img = pygame.image.load(choice(classes)).convert_alpha()
            self._enemy_img = pygame.image.load("client/assets/enemy.png").convert_alpha()
            self._bullet_img = pygame.image.load("client/assets/bullet.png").convert_alpha()
        except FileNotFoundError as e:
            print(f"Asset loading error: {e}")
            print("Please ensure player.png, enemy.png, and bullet.png are inside the 'assets' folder.")
            pygame.quit()
            sys.exit()

    def render(self, enemies: list, bullets: list, players: list) -> None:
        self.screen.fill(ARENA_BG)

        for ex, ey in enemies:
            self.screen.blit(self._enemy_img, (int(ex * self.scale), int(ey * self.scale)))

        for bx, by in bullets:
            self.screen.blit(self._bullet_img, (int(bx * self.scale), int(by * self.scale)))

        for px, py in players:
            self.screen.blit(self._player_img, (int(px * self.scale), int(py * self.scale)))

        pygame.display.flip()