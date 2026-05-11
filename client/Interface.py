"""Interface module for the game. This module defines the Interface class, which is responsible for managing the main game loop, handling user input, and coordinating the different components of the client."""

from time import time, sleep
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

        try:
            while not self.input_handler.quit:
                start_time = time()

                # Handle Input & Network
                input_msg = self.input_handler.build_input_msg()
                self.client.send(input_msg)

                # Prepare data for rendering
                my_player = self.game_state.my_player
                
                # If the server hasn't sent us our player info yet, we wait
                if my_player:
                    wave_data = self.game_state.wave
                    enemies_dict = wave_data.get("enemies", [])
                    enemies = [(e.get("x"), e.get("y")) for e in enemies_dict]
                    bullets = [(b.get("x"), b.get("y")) for b in self.game_state.bullets]
                    players = [(p.get("x"), p.get("y")) for p in self.game_state.players.values()]

                    # Render the frame
                    print(f"--- WASD to Move | Arrows to Shoot | ESC to Quit ---")
                    status = "ALIVE" if my_player.get("alive") else "DEAD"
                    print(f"Wave: {self.game_state.wave_number} | Status: {status}")
                    self.renderer.render(enemies, bullets, players)
                else:
                    print("Waiting for player initialization from server...")

                # Cap the Frame Rate
                elapsed = time() - start_time
                sleep_time = max(0, (1.0 / TICK_RATE) - elapsed)
                sleep(sleep_time)

                # Check if the game ended
                if self.game_state.event_game_over:
                    print("Game Over!")
                    break

                # Check if the player won
                if self.game_state.event_game_win:
                    print("You Win!")
                    break

        except KeyboardInterrupt:
            print("\nExiting game...")
        
        finally:
            self.client.disconnect()