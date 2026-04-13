"""
Server.py — Accepts TCP connections and runs the authoritative game loop.

Architecture
────────────
  • One ProcessClient(Thread) per connected socket — handles recv()
  • Server.run_game_loop() — single-threaded 60 Hz update loop
  • All mutation of GameState happens only inside the game loop
"""

import socket # usado para criar o socket do servidor e aceitar conexões TCP
import threading # usado para criar threads dedicadas para cada cliente, permitindo que o servidor processe múltiplos clientes simultaneamente sem bloqueio
import time # usado para controlar o tempo entre as atualizações do jogo e para calcular o delta time (dt) para a simulação do jogo

from shared.Constants  import SERVER_HOST, SERVER_PORT, MAX_PLAYERS, TICK_RATE # usado para definir as configurações do servidor, como o host e porta de escuta, o número máximo de jogadores e a taxa de atualização do jogo
from shared.Protocol   import (encode, MSG_WELCOME, MSG_STATE, MSG_BULLET_EVENTS,
                                MSG_WAVE_START, MSG_WAVE_CLEAR, MSG_SHOP_OPEN,
                                MSG_SHOP_CLOSE, MSG_GAME_OVER, MSG_GAME_WIN,
                                MSG_JOIN, MSG_BUY_UPGRADE, MSG_ERROR) # usado para definir as mensagens que o servidor pode enviar e receber, e para codificar as mensagens enviadas aos clientes
from server.ProcessClient import ProcessClient # usado para criar e gerenciar as threads de cada cliente, que lidam com a comunicação TCP e armazenam os inputs e comandos pendentes de cada jogador
from server.GameState     import GameState # usado para manter o estado do jogo, incluindo jogadores, inimigos, balas e ondas, e para atualizar o estado a cada tick com base nos inputs dos jogadores e nas regras do jogo


class Server:
    """
    Main server class.  Call server.start() to begin accepting connections
    and launch the game loop.
    """

    STATE_BROADCAST_RATE = 15   # state broadcasts per second

    def __init__(self, host: str = SERVER_HOST, port: int = SERVER_PORT):
        self.host = host
        self.port = port

        self.game_state = GameState()
        self._wire_callbacks()

        # {player_id: ProcessClient}
        self.clients: dict[int, ProcessClient] = {}
        self._pending_clients: list = []
        self._clients_lock = threading.Lock()
        self._next_pid = 0

        self._running = False

    # ── Public entry point 

    def start(self) -> None:
        """Bind, listen, launch game loop thread, accept connections."""
        srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv_sock.bind(("", self.port))
        srv_sock.listen(MAX_PLAYERS)
        print(f"[Server] Listening on {self.host}:{self.port}")

        self._running = True

        # Game loop in its own thread
        loop_thread = threading.Thread(target=self._game_loop, daemon=True)
        loop_thread.start()

        # Accept loop runs on the main thread
        while self._running:
            conn, addr = srv_sock.accept()
            self._accept_client(conn, addr)
        srv_sock.close()

    # ── Accept 

    def _accept_client(self, conn: socket.socket, addr: tuple) -> None:
        with self._clients_lock:
            if len(self.clients) >= MAX_PLAYERS:
                conn.sendall(encode({"type": MSG_ERROR, "msg": "Server full"}))
                conn.close()
                return

        pc = ProcessClient(conn, addr, self)
        pc.start()
        print(f"[Server] Client connected from {addr}; awaiting JOIN")

        with self._clients_lock:
            self._pending_clients.append(pc)

    # ── Disconnect callback (called from ProcessClient thread) 

    def on_client_disconnect(self, pc: ProcessClient) -> None:
        pid = pc.player_id
        print(f"[Server] Client disconnected pid={pid}")
        with self._clients_lock:
            if pc in self._pending_clients:
                self._pending_clients.remove(pc)
            if pid is not None:
                self.clients.pop(pid, None)
        if pid is not None:
            self.game_state.remove_player(pid)

    # ── Game loop 

    def _game_loop(self) -> None:
        tick_interval = 1.0 / TICK_RATE
        broadcast_every = 1.0 / self.STATE_BROADCAST_RATE
        last_time = time.time()
        last_broadcast = last_time

        while self._running:
            now = time.time()
            dt = now - last_time
            last_time = now

            # ── Process pending commands (JOIN, BUY_UPGRADE) 
            self._process_commands()

            # ── Build input snapshot for this tick 
            inputs = {}
            with self._clients_lock:
                for pid, pc in self.clients.items():
                    inputs[pid] = pc.get_input()

            # ── Advance game state 
            prev_bullet_ids = {b.id for b in self.game_state.bullets}
            self.game_state.update(dt, inputs)
            curr_bullets = self.game_state.bullets
            curr_ids = {b.id for b in curr_bullets}

            # Spawned = in current but not in prev; removed = in prev but not current
            spawned = [b.to_dict() for b in curr_bullets if b.id not in prev_bullet_ids]
            removed = list(prev_bullet_ids - curr_ids)

            if spawned or removed:
                self._broadcast({
                    "type": MSG_BULLET_EVENTS,
                    "spawn": spawned,
                    "remove": removed,
                })

            # ── Broadcast state at reduced rate 
            if now - last_broadcast >= broadcast_every:
                last_broadcast = now
                self._broadcast_state()

            # ── Sleep until next tick 
            elapsed = time.time() - now
            sleep = tick_interval - elapsed
            if sleep > 0:
                time.sleep(sleep)

    # ── Command processing 

    def _process_commands(self) -> None:
        with self._clients_lock:
            pending = list(self._pending_clients)
            all_pcs = list(self.clients.values()) + pending

        for pc in all_pcs:
            for cmd in pc.pop_commands():
                self._handle_command(pc, cmd)

    def _handle_command(self, pc: ProcessClient, cmd: dict) -> None:
        mtype = cmd.get("type")

        if mtype == MSG_JOIN:
            if pc.player_id is not None:
                return  # already joined

            class_id = int(cmd.get("class_id", 0)) % 7

            with self._clients_lock:
                if len(self.clients) >= MAX_PLAYERS:
                    pc.send({"type": MSG_ERROR, "msg": "Server full"})
                    return
                pid = self._next_pid
                self._next_pid += 1
                pc.player_id = pid
                self.clients[pid] = pc
                # Remove from pending
                if pc in self._pending_clients:
                    self._pending_clients.remove(pc)

            self.game_state.add_player(pid, class_id)
            state = self.game_state.to_dict()
            pc.send({"type": MSG_WELCOME,
                     "player_id": pid,
                     "state": state})
            print(f"[Server] Player joined as pid={pid} class={class_id}")

        elif mtype == MSG_BUY_UPGRADE:
            if pc.player_id is None:
                return
            upgrade = cmd.get("upgrade", "")
            p = self.game_state.players.get(pc.player_id)
            if p:
                ok = p.buy_upgrade(upgrade)
                if not ok:
                    pc.send({"type": MSG_ERROR, "msg": "Not enough coins"})

    # ── Broadcast 

    def _broadcast(self, msg: dict) -> None:
        with self._clients_lock:
            pcs = list(self.clients.values())
        for pc in pcs:
            pc.send(msg)

    def _broadcast_state(self) -> None:
        state = self.game_state.to_dict()
        self._broadcast({"type": MSG_STATE, "state": state})

    # ── Callbacks wired to GameState 

    def _wire_callbacks(self) -> None:
        self.game_state.on_wave_start.connect(self.handle_net_wave_start)
        self.game_state.on_wave_clear.connect(self.handle_net_wave_clear)
        self.game_state.on_shop_open.connect(self.handle_net_shop_open)
        self.game_state.on_shop_close.connect(self.handle_net_shop_close)
        self.game_state.on_game_over.connect(self.handle_net_game_over)
        self.game_state.on_game_win.connect(self.handle_net_game_win)

    def handle_net_wave_start(self, n: int) -> None:
        print(f"Server: wave {n} started")
        self._broadcast({"type": MSG_WAVE_START, "wave": n})

    def handle_net_wave_clear(self, n: int) -> None:
        print(f"Server: wave {n} cleared")
        self._broadcast({"type": MSG_WAVE_CLEAR, "wave": n})

    def handle_net_shop_open(self) -> None:
        print("Server: shop opened")
        self._broadcast({"type": MSG_SHOP_OPEN})

    def handle_net_shop_close(self) -> None:
        print("Server: shop closed")
        self._broadcast({"type": MSG_SHOP_CLOSE})

    def handle_net_game_over(self) -> None:
        print("Server: game over")
        self._broadcast({"type": MSG_GAME_OVER})

    def handle_net_game_win(self) -> None:
        print("Server: game win")
        self._broadcast({"type": MSG_GAME_WIN})