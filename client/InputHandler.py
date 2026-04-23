"""
InputHandler.py — Non-blocking keyboard listener using pynput.

WASD  → movement
Arrows → shooting direction
ESC   → quit
"""

from pynput import keyboard
from shared.Protocol import MSG_INPUT


class InputHandler:
    def __init__(self):
        self._keys = {
            "up": False, "down": False, "left": False, "right": False,
            "attack_up": False, "attack_down": False,
            "attack_left": False, "attack_right": False,
        }
        self._quit = False

        keys = self._keys

        def on_press(key):
            try:
                k = key.char.lower() if key.char else None
            except AttributeError:
                k = key

            if k == 'w': keys["up"]    = True
            if k == 's': keys["down"]  = True
            if k == 'a': keys["left"]  = True
            if k == 'd': keys["right"] = True

            if k == keyboard.Key.up:    keys["attack_up"]    = True
            elif k == keyboard.Key.down:  keys["attack_down"]  = True
            elif k == keyboard.Key.left:  keys["attack_left"]  = True
            elif k == keyboard.Key.right: keys["attack_right"] = True

            if k == keyboard.Key.esc:
                self._quit = True
                return False 

        def on_release(key):
            try:
                k = key.char.lower() if key.char else None
            except AttributeError:
                k = key

            if k == 'w': keys["up"]    = False
            if k == 's': keys["down"]  = False
            if k == 'a': keys["left"]  = False
            if k == 'd': keys["right"] = False

            if k == keyboard.Key.up:    keys["attack_up"]    = False
            elif k == keyboard.Key.down:  keys["attack_down"]  = False
            elif k == keyboard.Key.left:  keys["attack_left"]  = False
            elif k == keyboard.Key.right: keys["attack_right"] = False

        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.listener.start()

    @property
    def quit(self) -> bool:
        return self._quit

    def build_input_msg(self) -> dict:
        return {"type": MSG_INPUT, "keys": dict(self._keys)}