import time
from client.Client import Client
from client.GameState import ClientGameState
from client.InputHandler import InputHandler
from client.Renderer import Renderer
from shared.Constants import SCREEN_WIDTH, SCREEN_HEIGHT, SERVER_HOST, SERVER_PORT, TICK_RATE
from shared.Protocol import MSG_JOIN

def main():
    # Initialize core components
    game_state = ClientGameState()
    client = Client(SERVER_HOST, SERVER_PORT, game_state)
    input_handler = InputHandler()
    renderer = Renderer(game_state, SCREEN_WIDTH, SCREEN_HEIGHT)

    print(f"Connecting to server at {SERVER_HOST}:{SERVER_PORT}...")

    # Establish connection
    if not client.connect():
        print(f"Failed to connect: {client.error_msg}")
        return

    client.start_recv_thread()
    client.send({"type": MSG_JOIN})
    print("Connected! Waiting for game data...")

    try:
        while not input_handler.quit:
            start_time = time.time()

            # Handle Input & Network
            input_msg = input_handler.build_input_msg()
            client.send(input_msg)

            # Prepare data for rendering
            my_player = game_state.my_player
            
            # If the server hasn't sent us our player info yet, we wait
            if my_player:
                wave_data = game_state.wave
                enemies_dict = wave_data.get("enemies", [])
                enemies = [(e.get("x"), e.get("y")) for e in enemies_dict]
                bullets = [(b.get("x"), b.get("y")) for b in game_state.bullets]
                players = [(p.get("x"), p.get("y")) for p in game_state.players.values()]

                # Render the frame
                print(f"--- WASD to Move | Arrows to Shoot | ESC to Quit ---")
                status = "ALIVE" if my_player.get("alive") else "DEAD"
                print(f"Wave: {game_state.wave_number} | Status: {status}")
                renderer.render(enemies, bullets, players)
            else:
                print("Waiting for player initialization from server...")

            # Cap the Frame Rate
            elapsed = time.time() - start_time
            sleep_time = max(0, (1.0 / TICK_RATE) - elapsed)
            time.sleep(sleep_time)

            # Check if the game ended
            if game_state.event_game_over:
                print("\nGAME OVER!")
                break
            if game_state.event_game_win:
                print("\nYOU WIN!")
                break

    except KeyboardInterrupt:
        print("\nDisconnecting...")
    finally:
        # Cleanup
        client.disconnect()
        print("Client closed.")

if __name__ == "__main__":
    main()