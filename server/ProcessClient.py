"""
ProcessClient.py — Per-client receive thread.

Each connected socket gets its own ProcessClient(Thread) instance.
It reads raw data, decodes JSON frames, and routes messages to the
shared input buffer / command queue.

The server's main loop reads from those structures each tick.
"""

import socket # usado para gerenciar a conexão TCP com o cliente
import threading # usado para criar uma thread dedicada para cada cliente, permitindo que o servidor processe múltiplos clientes simultaneamente sem bloqueio

from shared.Protocol import decode, encode, MSG_INPUT # usado para decodificar as mensagens recebidas do cliente e para codificar as mensagens enviadas ao cliente


class ProcessClient(threading.Thread):
    """
    Runs in its own thread; owns the blocking recv() loop for one client.

    Public shared data (protected by locks set by Server):
      self.input       — latest input frame dict (keys/mouse/ability/shoot)
      self.commands    — list of pending non-input commands (join, buy, etc.)
      self.connected   — False once the socket is closed
      self.player_id   — assigned by Server after JOIN is processed
    """

    RECV_TIMEOUT = 5.0   # seconds; socket heartbeat interval

    def __init__(self, conn: socket.socket, addr: tuple, server_ref):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr
        self.server = server_ref

        # Each client gets its own lock for its input dict
        self.input_lock = threading.Lock()
        self.input: dict = {
            "keys": {"up": False, 
                     "down": False,
                     "left": False, 
                     "right": False,
                     "dash": False},
            "mouse": {"x": 0.0, 
                      "y": 0.0, 
                      "btn": False},
            "shoot": False,
            "ability": False,
        }

        # Non-realtime commands queued for the game loop
        self._cmd_lock = threading.Lock()
        self.commands: list[dict] = []

        self.connected = True
        self.player_id: int | None = None   # set by Server after JOIN

        self._recv_buf = b""

    # ── Thread entry point ────────────────────────────────────────────────────

    def run(self) -> None:
        """Main receive loop — runs until the client disconnects."""
        self.conn.settimeout(self.RECV_TIMEOUT)
        while self.connected:
            try:
                chunk = self.conn.recv(512)
            except socket.timeout:
                continue
            if not chunk:
                break

            self._recv_buf += chunk
            self._process_buffer()

        self.connected = False
        self.conn.close()

        # Notify server that this client is gone
        self.server.on_client_disconnect(self)

    # ── Buffer processing ─────────────────────────────────────────────────────

    def _process_buffer(self) -> None:
        """
        Extract complete newline-delimited JSON frames from the receive buffer
        and route each message.
        """
        messages = decode(self._recv_buf)
        # Keep only the incomplete tail (after the last newline)
        last_nl = self._recv_buf.rfind(b"\n")
        if last_nl >= 0:
            self._recv_buf = self._recv_buf[last_nl + 1:]
        else:
            self._recv_buf = b""
        for msg in messages:
            self._route(msg)

    def _route(self, msg: dict) -> None:
        mtype = msg.get("type")
        if mtype == MSG_INPUT:
            # Update latest input frame 
            with self.input_lock:
                keys  = msg.get("keys", {})
                mouse = msg.get("mouse", {})
                self.input = {
                    "keys": {
                        "up":    bool(keys.get("up")),
                        "down":  bool(keys.get("down")),
                        "left":  bool(keys.get("left")),
                        "right": bool(keys.get("right")),
                        "dash":  bool(keys.get("dash")),
                    },
                    "mouse": {
                        "x":   float(mouse.get("x", 0)),
                        "y":   float(mouse.get("y", 0)),
                        "btn": bool(mouse.get("btn")),
                    },
                    "shoot":   bool(msg.get("shoot", mouse.get("btn", False))),
                    "ability": bool(msg.get("ability")),
                }
            return

        # Everything else goes onto the command queue
        with self._cmd_lock:
            self.commands.append(msg)

    # ── Sending ───────────────────────────────────────────────────────────────

    def send(self, msg: dict) -> None:
        """Send a message to this client."""
        self.conn.sendall(encode(msg))

    # ── Command queue access ──────────────────────────────────────────────────

    def pop_commands(self) -> list[dict]:
        """Drain and return all pending commands atomically."""
        with self._cmd_lock:
            cmds, self.commands = self.commands, []
        return cmds

    def get_input(self) -> dict:
        """Return a deep snapshot of the latest input frame."""
        with self.input_lock:
            inp = self.input
            return {
                "keys":    dict(inp["keys"]),
                "mouse":   dict(inp["mouse"]),
                "shoot":   inp["shoot"],
                "ability": inp["ability"],
            }