"""Interface module for the game. This module defines the Interface class, which is responsible for managing the main game loop, handling user input, and coordinating the different components of the client."""

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

        # Establish connection
        if not self.client.connect():
            print("Failed to connect.")
            return

        # Start the receiver thread to listen for server messages
        self.client.start_recv_thread()
        self.client.send({"type": MSG_JOIN})
        print("Connected! Waiting for game data...")

        # Set up a Pygame clock to manage frame rate cleanly
        clock = pygame.time.Clock()

        try:
            while not self.input_handler.quit:
                # 1. Pump and handle Pygame events (Keyboard, window closing, etc.)
                self.input_handler.handle_events()
                
                if self.input_handler.quit:
                    break

                # 2. Handle Network Send
                input_msg = self.input_handler.build_input_msg()
                self.client.send(input_msg)

                # 3. Prepare data for rendering
                my_player = self.game_state.my_player
                
                # If the server hasn't sent us our player info yet, we wait
                if my_player:
                    wave_data = self.game_state.wave
                    enemies_dict = wave_data.get("enemies", [])
                    enemies = [(e.get("x"), e.get("y")) for e in enemies_dict]
                    bullets = [(b.get("x"), b.get("y")) for b in self.game_state.bullets]
                    players = [(p.get("x"), p.get("y")) for p in self.game_state.players.values()]

                    # Update window title with status details dynamically
                    status = "ALIVE" if my_player.get("alive") else "DEAD"
                    pygame.display.set_caption(
                        f"Multiplayer Arena | Wave: {self.game_state.wave_number} | Status: {status}"
                    )

                    # Render the graphical frame using Pygame blit
                    self.renderer.render(enemies, bullets, players)
                else:
                    # Keep Pygame responsive while waiting for the server
                    self.renderer.screen.fill((12, 15, 28)) # Fallback clear screen
                    pygame.display.flip()

                # 4. Check game termination events
                if self.game_state.event_game_over:
                    print("Game Over!")
                    break

                if self.game_state.event_game_win:
                    print("You Win!")
                    break

                # 5. Cap the Frame Rate using Pygame's built-in tick manager
                clock.tick(TICK_RATE)

        except KeyboardInterrupt:
            print("\nExiting game...")
        
        finally:
            self.client.disconnect()
            pygame.quit()  # Clean up Pygame windows and audio drivers safely