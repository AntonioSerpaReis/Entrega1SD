import pygame
from client.Client import Client
from client.GameState import ClientGameState
from client.InputHandler import InputHandler
from client.Renderer import Renderer
from client import SCREEN_WIDTH, SCREEN_HEIGHT, SERVER_HOST, SERVER_PORT, TICK_RATE, MSG_JOIN

class Interface:
    def __init__(self):
        self.game_state = ClientGameState()
        self.client = Client(SERVER_HOST, SERVER_PORT, self.game_state)
        self.input_handler = InputHandler()
        self.renderer = Renderer(self.game_state, SCREEN_WIDTH, SCREEN_HEIGHT)

    def run(self):
        print(f"Connecting to server at {SERVER_HOST}:{SERVER_PORT}...")

        if not self.client.connect():
            print("Failed to connect.")
            return

        self.client.start_recv_thread()
        self.client.send({"type": MSG_JOIN})
        print("Connected! Waiting for game data...")

        clock = pygame.time.Clock()

        try:
            while not self.input_handler.quit:
                self.input_handler.handle_events()
                
                if self.input_handler.quit:
                    break

                input_msg = self.input_handler.build_input_msg()
                self.client.send(input_msg)

                my_player = self.game_state.my_player
                
                if my_player:
                    wave_data = self.game_state.wave
                    enemies_dict = wave_data.get("enemies", [])
                    enemies = [(e.get("x"), e.get("y")) for e in enemies_dict]
                    bullets = [(b.get("x"), b.get("y")) for b in self.game_state.bullets]
                    players = [(p.get("x"), p.get("y")) for p in self.game_state.players.values()]

                    status = "ALIVE" if my_player.get("alive") else "DEAD"
                    pygame.display.set_caption(
                        f"Multiplayer Arena | Wave: {self.game_state.wave_number} | Status: {status}"
                    )
                    self.renderer.render(enemies, bullets, players)

                if self.game_state.event_game_over:
                    print("Game Over!")
                    break

                if self.game_state.event_game_win:
                    print("You Win!")
                    break

                clock.tick(TICK_RATE)

        except KeyboardInterrupt:
            print("\nExiting game...")
        
        finally:
            self.client.disconnect()
            pygame.quit()