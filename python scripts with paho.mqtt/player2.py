import paho.mqtt.client as mqtt
import random
import time

PLAYER_SYMBOL = 'O'

game_over = False
TOPIC_MOVES = "tic-tac-toe/moves"
TOPIC_SYNC = "tic-tac-toe/sync"
TOPIC_GAME_OVER = "tic-tac-toe/gameover"
TOPIC_PLAYER_CONNECT = "tic-tac-toe/player/connect"

current_board = [['', '', ''], ['', '', ''], ['', '', '']]

def make_move():
    """Make a random move on the board."""
    empty_cells = [(i, j) for i in range(3) for j in range(3) if current_board[i][j] == '']
    if empty_cells:
        i, j = random.choice(empty_cells)
        current_board[i][j] = PLAYER_SYMBOL
        print(f"Making a move at ({i}, {j}) with symbol {PLAYER_SYMBOL}")
        time.sleep(1)
        client.publish(TOPIC_MOVES, f"{i},{j},{PLAYER_SYMBOL}")
    else:
        print("No empty cells found!")

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker."""
    if rc == 0:
        print(f"Connected successfully as Player {1 if PLAYER_SYMBOL == 'X' else 2}.")
        client.publish(TOPIC_PLAYER_CONNECT, f"Player {1 if PLAYER_SYMBOL == 'X' else 2}")
        client.subscribe(TOPIC_GAME_OVER)
        client.subscribe(TOPIC_SYNC)
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    """Callback for when a message is received from the broker."""
    topic = msg.topic
    payload = msg.payload.decode()

    if topic == TOPIC_SYNC and payload == PLAYER_SYMBOL:
        make_move()
    elif topic == TOPIC_GAME_OVER:
        global game_over
        print(payload)
        game_over = True
        reconnect()
    elif topic == TOPIC_MOVES:
        # Update the current_board based on moves made by both players
        x, y, symbol = map(str, payload.split(','))
        x, y = int(x), int(y)
        current_board[x][y] = symbol


def reconnect():
    """Reconnect the player to the game."""
    global game_over, current_board
    game_over = False
    current_board = [['', '', ''], ['', '', ''], ['', '', '']]
    client.disconnect()
    time.sleep(2)
    client.connect("localhost", 1883, 60)

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)
    client.loop_start()

    while True:
        time.sleep(2)
