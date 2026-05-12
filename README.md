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
* **Mecânica One-Hit:** Não existe HP. Tanto jogadores como inimigos estão ou **Vivos** ou **Mortos**.
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
* **`servidor/`**: Processa a lógica de jogo e inputs de todos os clientes.

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

## Arquitetura do Sistema
O projeto é dividido em dois componentes principais: **Cliente** (responsável pela interface e entrada do usuário) e **Servidor** (responsável pela lógica do jogo, colisões e sincronização de estado).


##  Cliente (Client-Side)

### `Client`
**Descrição:** Gere a conexão de rede com o servidor.
- **Atributos:**
    - `host`: Endereço ipv4 do maquina servidor
    - `port`: porta de conexão
    - `_sock` (socket TCP): socket do cliente
    - `_receiver` (thread de escuta): Referencia do Receiver
    - `_send_lock`: Lock para manter a integridade da informação quando se enviam mensagens para o servidor
    - `gs`: Referência do GameState lado do cliente
    - `error_msg`: Mensagem de erro caso tenha dado erro (a conectar ao servidor por exemplo)
- **Métodos:**
    - `connect()`: Estabelece conexão com o IP/Porta alvo.
    - `start_recv_thread()`: Inicia a thread `Receiver`.
    - `disconnect()`: Encerra a conexão e limpa recursos.
    - `connected()`: Retorna o status da conexão.
    - `send(msg)`: Envia dados serializados ao servidor de forma thread-safe.

### `Interface`
**Descrição:** Thread principal do lado do cliente.
- **Atributos:**
    - `game_state`: Referencia do GameState lado do cliente
    - `client`: Referencia do Client
    - `input_handler`: Referencia do InputHandler
    - `renderer`: Referencia do Renderer
- **Métodos:**
    - `run()`: Loop principal que processa inputs do cliente e renderiza a tela.

### `GameState`
**Descrição:** Armazena o estado atual do jogo recebido do servidor.
- **Atributos:**
    - `phase`: Fase atual do jogo
    - `players` (dict): Tuplo de endereço do jogador passado para string -> Informação do player (dict)
    - `wave`: onda atual
    - `bullets` (list): Informação da bala (dict) 
    - `my_player_id`: Tuplo de endereço do jogador passado para string
    - `event_wave_clear` (bool): Estado wave clear
    - `event_game_over` (bool): Estado game over
    - `event_game_win` (bool): Estado game win
- **Métodos:**
    - `apply_state(data)`: Atualiza os atributos locais com o dicionário vindo do servidor.
    - `my_player()`: Retorna o objeto do jogador local.
    - `wave_number()`: Retorna o número da onda atual.
    - `enemies()`: Lista de inimigos ativos.

### `InputHandler`
**Descrição:** Captura eventos de teclado do utilizador.
- **Atributos:**
    - `_keys` (set de teclas pressionadas)
    - `_quit`
    - `listener` (thread de escuta do teclado)
- **Métodos:**
    - `on_press(key)` / `on_release(key)`: Callbacks para monitorização de teclas.
    - `quit()`: Sinaliza o encerramento.
    - `build_input_msg()`: Transforma teclas pressionadas em comandos para o servidor.

### `Receiver` (Thread)
**Descrição:** Escuta continuamente mensagens do servidor para atualizar o GameState do lado do cliente.
- **Atributos:**
    - `_sock`: socket do cliente (AF_INET, SOCK_STREAM)
    - `gs`: Referencia do GameState do lado do Cliente para atualização com _process(data)
- **Métodos:**
    - `run()`: Loop de recepção `recv`.
    - `_process(data)`: Desserializa e encaminha dados para o `GameState`.

### `Renderer`
**Descrição:** Responsável pela saída visual (CLI ou Gráfica).
- **Atributos:**
    - `_width`: Comprimento da janela/arena
    - `_height`: Altura da janela/arena
    - `_gs`: Informação do estado do jogo (Referencia do GameState lado do cliente)
- **Métodos:**
    - `_clear_screen()`: Limpa o ecrã de visualização.
    - `render()`: Desenha a arena, jogadores, balas e UI com base no `GameState`.

## Servidor (Server-Side)

### `Server`
**Descrição:** Ponto de entrada do servidor e orquestrador de rede.
- **Atributos:**
    - `_socket`: Socket do servidor (AF_INET, SOCK_STREAM)
    - `_game_state`: Referencia do GameState
    - `_clients`: Referencia da ClientList
    - `_broadcaster`: Referencia do Broadcaster
    - `_running`: Estado do servidor (Está a correr ou não)
- **Métodos:**
    - `run()`: Inicializa o socket e aceita novas conexões.
    - `_interrupt_for_clients()`: Interrupção do jogo para aceitar clientes
    - `_run_game_loop()`: Loop de física e lógica (update global).

### `ProcessClient` (Thread)
**Descrição:** Lida com a comunicação individual de cada jogador conectado.
- **Atributos:**
    - `conn`: Conexão do jogador
    - `addr`: Tuplo de endereço do jogador
    - `player_id`: Identificador único (Tuplo de endereço do jogador passado para string)
    - `game_state`: Referencia do GameState
    - `clients`: Referencia da ClientList
- **Métodos:**
    - `run()`: Recebe inputs do cliente.
    - `_route(msg)`: Encaminha a mensagem para o handler correto (Join, Move, Shoot).
    - `_apply_input(input_data)`: Atualiza a intenção de movimento/ação do `Player`.

### `GameState` (Server)
**Descrição:** Gere a lógica de física e colisões.
- **Atributos:**
    - `players`: Jogadores
    - `bullets`: Balas
    - `wave_mgr`: Referencia do WaveManager
    - `running`: Estado do jogo (se acabou ou não)
    - `phase`: Fase atual do jogo
    - `lock`: Lock para manter integridade da informação quando se adiciona/remove jogadores/atualiza estado do jogo
- **Métodos:**
    - `add_player(id)` / `remove_player(id)`: Gestão de entidades.
    - `update()`: Move todas as entidades, processa disparos e verifica colisões.
    - `to_dict()`: Serializa o estado completo para envio. (Fase Atual, Inimigos, Jogadores, Balas)

### `ClientList`
**Descrição:** Gerenciador thread-safe da lista de conexões ativas.
- **Atributos:**
    - `clients` (dict)
    - `_lock`: Lock para manter a integridade da informação quando se remove/adiciona/pegar
- **Métodos:**
    - `add()`: Adiciona cliente à lista
    - `remove()`: Remove cliente da lista
    - `get_all()`: Pega os clientes da lista sem remover

### `Broadcaster` (Thread)
**Descrição:** Envia o estado atual do jogo para todos os clientes em intervalos regulares (Tick Rate).
- **Atributos:**
    - `client_list`: Lista de clientes (referencia para a lista de clientes)
    - `game_state`: Estado do jogo (referencia para o GameState)
    - `interval`: Intervalo de envio de informação para os clientes
- **Métodos:**
    - `broadcast_state()`: Envia o `GameState.to_dict()` para todos os sockets/clientes.

### `WaveManager`
**Descrição:** Controla o progresso das fases e spawn de inimigos.
- **Atributos:**
    - `wave_number`: Onda atual
    - `enemies`: Inimigos atuais
    - `state`: Estado atual
- **Métodos:**
    - `start_next_wave()`: Gera novos inimigos.
    - `all_dead()`: Verifica se a onda foi limpa.
    - `to_dict()`: Retorna status da onda.

### `Enemy`
**Descrição:** Entidade hostil controlada por IA simples.
- **Atributos:**
    - `id`: ID unico (uuid)
    - `x`, `y`: Posição atual
    - `alive`: Estado atual
    - `target_x`, `target_y`: Para onde ele vai
    - `speed`: Vetor de velocidade
- **Métodos:**
    - `update()`: Lógica de movimentação random.
    - `take_damage(amount)`: Reduz vida e verifica morte.

### `Player`
**Descrição:** Representação do jogador no servidor.
- **Atributos:**
    - `player_id`: Identificador único (Tuplo de endereço do jogador passado para string)
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
    - `id`: ID único. (uuid)
    - `x`, `y`: Posição atual.
    - `vx`, `vy`: Vetores de velocidade (direção).
    - `lifetime`: Tempo de vida restante antes de desaparecer.
    - `alive`: Status de atividade.
- **Métodos:**
    - `update()`: Atualiza a posição com base na velocidade e decrementa o `lifetime`.
    - `despawn()`: Marca a bala como inativa para remoção do GameState.
    - `overlaps(target)`: Verifica colisão circular ou retangular com um `Enemy`.
    - `to_dict()`: Serializa dados (x, y, id) para renderização no cliente.


## Tecnologias Utilizadas
- **Linguagem:** Python 3.13.13
- **Comunicação:** socket (TCP/IP)
- **Geração de IDs:** Módulo uuid
- **Concorrência:** Multi-threading (módulo `threading`)
- **Física:** `random` (movimentação/inserção dos inimigos e inserção dos players), `time` (para atualizar o estado do jogo)
- **Serialização:** JSON

---
> *Este é um projeto desenvolvido para fins estritamente académicos.*
