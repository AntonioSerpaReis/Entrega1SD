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
O projeto está dividido em três módulos principais para garantir a separação de responsabilidades:

* **`cliente/`**: Gere os inputs do jogador e a renderização local.
* **`servidor/`**: O "Cérebro" do projeto. Processa a lógica de jogo e inputs de todos os clientes.
* **`shared/`**: Biblioteca comum com protocolos de comunicação e constantes globais.

### Comunicação
* **Servidor:** Envia um *broadcast* contínuo do estado global do jogo para todos os clientes ligados.
* **Cliente:** Envia continuamente os eventos de input (teclas premidas) para o servidor.

---

## Condições de Jogo
* **Vitória:** Limpar as 10 waves de inimigos.
* **Derrota:** Todos os jogadores serem eliminados (estado "morto").
* **Pontuação:** Baseada no número de ondas (waves) concluídas com sucesso.

---
> *Este é um projeto desenvolvido para fins estritamente académicos.*