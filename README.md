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

cliente: Onde é gerido os inputs do cliente e os outputs do servidor

servidor: Onde são processados os inputs dos clientes

shared: Onde estão os protocolos e constantes
