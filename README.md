# Winx: Bullet Hell

Projeto académico de um jogo multiplayer cooperativo focado em sobrevivência por ondas, desenvolvido com foco em arquitetura cliente-servidor.

---

## Grupo
* **António Reis**
* **Leandro Cosme**

---

## O Jogo
O objetivo é simples: sobreviver. Até **7 jogadores** devem cooperar para derrotar hordas de IAs em uma arena fechada.

### Funcionalidades
* **Natureza Cooperativa:** Jogadores vs. IA (sem PvP).
* **Sistema de Waves:** O jogo possui 10 níveis/ondas de dificuldade progressiva.
* **Mecânica One-Hit:** Não existe HP. Tanto jogadores como inimigos estão ou **Vivos** ou **Mortos**, por enquanto.
* **Dificuldade Dinâmica:** Quanto maior a pontuação, mais desafiante o jogo se torna.
* **Evolução Visual:** Atualmente executado no terminal, com transição planeada para interface gráfica via **Pygame** (câmera estática).

---

## Controlos

| Comando | Teclas |
| :--- | :--- |
| **Movimentação** | `W` `A` `S` `D` |
| **Disparar** | `Setas Direcionais` |

---

## Arquitetura do Sistema
O projeto está dividido em dois módulos principais para garantir a separação de responsabilidades:

* **`cliente/`**: Gere os inputs do jogador e a renderização local.
* **`servidor/`**: O "Cérebro" do projeto. Processa a lógica de jogo e inputs de todos os clientes.

### Comunicação
* **Servidor:** Envia um *broadcast* contínuo do estado global do jogo para todos os clientes ligados.
* **Cliente:** Envia continuamente os eventos de input (teclas premidas) para o servidor.

---

## Condições de Jogo
* **Vitória:** Limpar as 10 waves de inimigos.
* **Derrota:** Todos os jogadores serem eliminados (estado "morto").
* **Pontuação:** Baseada no número de ondas (waves) concluídas com sucesso.

# Winx: Bullet Hell - Documentação do Projeto

Projeto de um jogo estilo *Bullet Hell* multiplayer utilizando arquitetura Cliente-Servidor com Sockets e Threads em Python.

## 🚀 Arquitetura do Sistema
O projeto é dividido em dois componentes principais: **Cliente** (responsável pela interface e entrada do usuário) e **Servidor** (responsável pela lógica do jogo, colisões e sincronização de estado).

---

## 🖥️ Cliente (Client-Side)

### `Client`
**Descrição:** Gere a conexão de rede de baixo nível com o servidor.
- **Atributos:** `host`, `port`, `_sock` (socket TCP), `_receiver` (thread de escuta), `_send_lock`, `gs` (referência ao GameState), `error_msg`.
- **Métodos:**
    - `connect()`: Estabelece conexão com o IP/Porta alvo.
    - `start_recv_thread()`: Inicia a thread `Receiver`.
    - `disconnect()`: Encerra a conexão e limpa recursos.
    - `connected()`: Retorna o status da conexão.
    - `send(msg)`: Envia dados serializados ao servidor de forma thread-safe.

### `Interface`
**Descrição:** Orquestrador principal do lado do cliente.
- **Atributos:** `game_state`, `client`, `input_handler`, `renderer`.
- **Métodos:**
    - `run()`: Loop principal que processa inputs e renderiza a tela.

### `GameState`
**Descrição:** Armazena a "foto" atual do jogo recebida do servidor.
- **Atributos:** `phase`, `players`, `wave`, `bullets`, `my_player_id`, `event_wave_clear`, `event_game_over`, `event_game_win`.
- **Métodos:**
    - `apply_state(data)`: Atualiza os atributos locais com o dicionário vindo do servidor.
    - `my_player()`: Retorna o objeto do jogador local.
    - `wave_number()`: Retorna o número da onda atual.
    - `enemies()`: Lista de inimigos ativos.

### `InputHandler`
**Descrição:** Captura eventos de teclado do utilizador.
- **Atributos:** `_keys` (set de teclas pressionadas), `_quit`, `listener`.
- **Métodos:**
    - `on_press(key)` / `on_release(key)`: Callbacks para monitorização de teclas.
    - `quit()`: Sinaliza o encerramento.
    - `build_input_msg()`: Transforma teclas pressionadas em comandos para o servidor.

### `Receiver` (Thread)
**Descrição:** Escuta continuamente mensagens do servidor para atualizar o GameState local.
- **Atributos:** `_sock`, `gs`.
- **Métodos:**
    - `run()`: Loop de recepção `recv`.
    - `_process(data)`: Desserializa e encaminha dados para o `GameState`.

### `Renderer`
**Descrição:** Responsável pela saída visual (CLI ou Gráfica).
- **Atributos:** `_width`, `_height`, `_gs`.
- **Métodos:**
    - `_clear_screen()`: Limpa o buffer de visualização.
    - `render()`: Desenha a arena, jogadores, balas e UI com base no `GameState`.

---

## ⚙️ Servidor (Server-Side)

### `Server`
**Descrição:** Ponto de entrada do servidor e orquestrador de rede.
- **Atributos:** `_socket`, `_game_state`, `_clients`, `_broadcaster`, `_running`.
- **Métodos:**
    - `run()`: Inicializa o socket e aceita novas conexões.
    - `_run_game_loop()`: Loop de física e lógica (update global).

### `ProcessClient` (Thread)
**Descrição:** Lida com a comunicação individual de cada jogador conectado.
- **Atributos:** `conn`, `addr`, `player_id`, `game_state`, `clients`.
- **Métodos:**
    - `run()`: Recebe inputs do cliente.
    - `_route(msg)`: Encaminha a mensagem para o handler correto (Join, Move, Shoot).
    - `_apply_input(input_data)`: Atualiza a intenção de movimento/ação do `Player`.

### `GameState` (Server)
**Descrição:** A "fonte da verdade" do jogo. Gere a lógica de física e colisões.
- **Atributos:** `players`, `bullets`, `wave_mgr`, `running`, `phase`, `lock`.
- **Métodos:**
    - `add_player(id)` / `remove_player(id)`: Gestão de entidades.
    - `update()`: Move todas as entidades, processa disparos e verifica colisões.
    - `to_dict()`: Serializa o estado completo para envio.

### `ClientList`
**Descrição:** Gerenciador thread-safe da lista de conexões ativas.
- **Atributos:** `clients` (dict), `_lock`.
- **Métodos:** `add()`, `remove()`, `get_all()`.

### `Broadcaster` (Thread)
**Descrição:** Envia o estado atual do jogo para todos os clientes em intervalos regulares (Tick Rate).
- **Atributos:** `client_list`, `game_state`, `interval`.
- **Métodos:**
    - `broadcast_state()`: Envia o `GameState.to_dict()` para todos os sockets.

### `WaveManager`
**Descrição:** Controla o progresso das fases e spawn de inimigos.
- **Atributos:** `wave_number`, `enemies`, `state`.
- **Métodos:**
    - `start_next_wave()`: Gera novos inimigos.
    - `all_dead()`: Verifica se a onda foi limpa.
    - `to_dict()`: Retorna status da onda.

### `Enemy`
**Descrição:** Entidade hostil controlada por IA simples.
- **Atributos:** `id`
- `x`, `y`
- `alive`
- `target_x`, `target_y`
- `speed`:
- **Métodos:**
    - `update()`: Lógica de movimentação (random ou target).
    - `take_damage(amount)`: Reduz vida e verifica morte.

### `Player`
**Descrição:** Representação do jogador no servidor.
- **Atributos:**
- `player_id`: Identificador único (Endereço do jogador "")
- `x`, `y`: Posição atual.
- `speed`: Vetor de velocidade
- `alive`: Status de atividade.
- `fire_cd_end`: Intervalo entre disparo de balas
- `latest_input`: Ultimo input do jogador
- **Métodos:**
    - `update()`: Aplica movimento baseado no `latest_input`.
    - `_shoot()`: Instancia objetos `Bullet` no `GameState`.

### `Bullet`
**Descrição:** Projéteis disparados por jogadores.
- **Atributos:**
    - `id`: Identificador único.
    - `x`, `y`: Posição atual.
    - `vx`, `vy`: Vetores de velocidade (direção).
    - `lifetime`: Tempo de vida restante antes de desaparecer.
    - `alive`: Status de atividade.
- **Métodos:**
    - `update()`: Atualiza a posição com base na velocidade e decrementa o `lifetime`.
    - `despawn()`: Marca a bala como inativa para remoção do GameState.
    - `overlaps(target)`: Verifica colisão circular ou retangular com um `Enemy`.
    - `to_dict()`: Serializa dados (x, y, id) para renderização no cliente.

---

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python 3.13.13
- **Comunicação:** socket TCP/IP
- **Geração de IDs:** Módulo uuid
- **Concorrência:** Multi-threading (módulo `threading`)
- **Serialização:** JSON

---
> *Este é um projeto desenvolvido para fins estritamente académicos.*
