# Projeto académico de um jogo multiplayer.

## Grupo:

António Reis

Leandro Cosme

## Features:

O jogo terá uma natureza de cooperação, isto é, os jogadores não lutam entre si, mas sim contra AIs

O jogo terá 7 players no máximo. 

O jogo terá um nível que se repete até 10 vezes.

O jogo irá decorrer, eventualmente, numa arena fechada com uma câmera estática, isto é, o que é visto a se mover são os jogadores, os inimigos e as balas, mas não a arena.

Os jogadores podem escolher uma classe (de 7 diferentes), cada classe com uma abilidade diferente.

O jogador poderá se melhorar com melhorias compradas na loja, acessada depois de completar a wave, com as moedas recebidas no final de cada wave.

Mecânica de Invulnerabilidade: Quando o jogador leva com uma bullet, entra num estado de invulnerabilidade onde não leva dano por x tempo. Isto foi implementado para o jogador não receber muitas balas de uma vez e ser derrotado instantaneamente.

A loja terá vários upgrades disponíveis.

A pontuação será o número de waves limpas e o jogo termina caso os jogadores limpem as 10 waves ou sejam todos derrotados

Quanto maior a pontuação, mais difícil o jogo fica

## Controlos:

WASD - para movimentação

LSHIFT - para dar dash

SPACE - para usar abilidades

MOUSE - para apontar e disparar

## Arquitetura do sistema:

O nosso jogo está dividido em 3 módulos:

cliente: Onde é gerido os inputs do cliente

servidor: Onde são processados os inputs dos clientes

shared: Onde estão os protocolos e constantes necessários tanto para o servidor como para o cliente.

## Comunicação cliente-servidor:

Servidor: Dá broadcast continuamente do estado do jogo

Cliente: Dá continuamente ao servidor os botões que foram apertados pelo cliente

## O que falta?

A parte gráfica (A arena, os inimigos, as classes e as bullets) que é o que define o nome do jogo Winx:Bullet Hell.

Execução do jogo para fins de execução de testes.

Balanceamento do jogo. O jogo é capaz de estar desbalanceado porque nós fizemos o jogo a olho. Devido à falta de execução do jogo não foi possível testar se o jogo está muito fácil ou muito díficil.

__main__.py tanto do servidor como do cliente para executar (Como não implementamos a parte gráfica, achamos melhor implementar depois de aprendermos pygame para se ver o jogo a correr e fazer os testes)
