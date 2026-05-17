import json

# Configurações do servidor
SERVER_HOST = "localhost"
SERVER_PORT = 5555
MAX_PLAYERS = 7

# Tamanho da arena/janela de jogo
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 40

# Constantes de jogo
TICK_RATE = 5
BULLET_SPEED = 5
PLAYER_SPEED = 5
ENEMY_SPEED = 3
ENEMIES_PER_WAVE_BASE  = 6
ENEMIES_PER_WAVE_SCALE = 3

# Protocolos
MSG_JOIN = "join"
MSG_INPUT = "input"
MSG_WELCOME = "welcome"
MSG_STATE = "state" 

#Métodos de receção e envio de mensagens
INT_SIZE = 8

def receive_int(connection) -> int:
    """
    :param n_bytes: The number of bytes to read from the current connection
    :return: The next integer read from the current connection
    """
    data = connection.recv(INT_SIZE)
    return int.from_bytes(data, byteorder='big', signed=True)

def send_int(connection, value: int) -> None:
    """
    :param value: The integer value to be sent to the current connection
    :param n_bytes: The number of bytes to send
    """
    connection.send(value.to_bytes(INT_SIZE, byteorder="big", signed=True))

def send_object(connection, obj):
    """1º: envia tamanho, 2º: envia dados."""
    data = json.dumps(obj).encode('utf-8')
    size = len(data)
    send_int(connection, size)    
    connection.send(data)              		     

def receive_object(connection):
    """1º: lê tamanho, 2º: lê dados."""
    size = receive_int(connection)
    data = connection.recv(size)
    result = json.loads(data.decode('utf-8'))
    return result