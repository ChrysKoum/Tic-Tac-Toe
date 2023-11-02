import paho.mqtt.client as mqtt
import random
import time

# Define board and topics
board = [['', '', ''], ['', '', ''], ['', '', '']]
game_over = False
game_started = False
TOPIC_MOVES = "tic-tac-toe/moves"
TOPIC_SYNC = "tic-tac-toe/sync"
TOPIC_GAME_OVER = "tic-tac-toe/gameover"
TOPIC_PLAYER_CONNECT = "tic-tac-toe/player/connect"
connected_players = set()

def is_winner(symbol):
    """Check if the given player has won."""
    # Check rows, columns, diagonals
    for i in range(3):
        if all([cell == symbol for cell in board[i]]) or all([board[j][i] == symbol for j in range(3)]):
            return True

    # Check both diagonals
    return board[0][0] == board[1][1] == board[2][2] == symbol or \
           board[0][2] == board[1][1] == board[2][0] == symbol


def is_board_full():
    """Check if the board is full."""
    return all(cell != '' for row in board for cell in row)

def handle_moves(payload):
    global game_over, game_started
    
    if game_over or not game_started:
        print("Game has not started or has ended. Waiting for players to reconnect.")
        return

    x, y, symbol = map(str, payload.split(','))
    x, y = int(x), int(y)

    if board[x][y] == '':
        board[x][y] = symbol
        print_board()  # Print the board after every move
        time.sleep(1)  # For better track of the moves a 1-second delay
        if is_winner(symbol):
            end_game(f"Player {symbol} wins!")
        elif is_board_full():
            end_game("It's a tie!")
        else:
            next_turn = 'O' if symbol == 'X' else 'X'
            print(f"It's Player {next_turn}'s turn!")
            client.publish(TOPIC_SYNC, next_turn)
    else:
        # If the move is invalid, request the same player to make another move
        print(f"Invalid move by Player {symbol} at ({x}, {y}). Requesting another move.")
        client.publish(TOPIC_SYNC, symbol)


def print_board():
    """Display the current state of the board."""
    for row in board:
        print("|".join([' ' + cell + ' ' for cell in row]))
        print("-" * 9)

def reset_board():
    """Reset the game state."""
    global board, connected_players, game_over, game_started
    board = [['', '', ''], ['', '', ''], ['', '', '']]
    connected_players = set()
    game_over = False
    game_started = False

def end_game(message):
    """End the current game and reset the board."""
    global game_over
    print(message)
    client.publish(TOPIC_GAME_OVER, message)
    game_over = True
    print("To restart the game, both players need to reconnect.")
    reset_board()

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker."""
    if rc == 0:
        print("Connected successfully.")
        client.subscribe(TOPIC_MOVES)
        client.subscribe(TOPIC_PLAYER_CONNECT)
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    """Callback for when a message is received from the broker."""
    global connected_players
    topic = msg.topic
    payload = msg.payload.decode()

    if topic == TOPIC_MOVES:
        handle_moves(payload)
    elif topic == TOPIC_PLAYER_CONNECT:
        connected_players.add(payload)
        print(f"{payload} is connected!")
        if len(connected_players) == 2:
            print("The two players are Connected!!")
            time.sleep(2)  
            start_game()

def start_game():
    global game_started
    game_started = True
    time.sleep(1)  
    starting_player = 1 if random.choice([True, False]) else 2
    starting_symbol = 'X' if starting_player == 1 else 'O'
    print(f"Player {starting_player} ('{starting_symbol}') starts!")
    client.publish(TOPIC_SYNC, starting_symbol)




if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)
    client.loop_start()
    
    while True:
        time.sleep(2)
