import random
import time
import sys

from commlib.msg import PubSubMessage, RPCMessage
from commlib.node import Node, TransportType

# Define board and topics
board = [['', '', ''], ['', '', ''], ['', '', '']]
game_over = False
game_started = False
connected_players = set()

class BoardStatusMessage(PubSubMessage):
    board: list[list[str]]

class MovesMessage(PubSubMessage):
    x: int = 0
    y: int = 0
    symbol: str = 'X'

class SyncMessage(PubSubMessage):
    symbol: str = 'X'

class PlayerConnectMessage(PubSubMessage):
    player: str = 'X'

class GameOverMessage(PubSubMessage):
    game_over: bool = 'False'
    message: str = 'start'

def is_winner(symbol):
    for i in range(3):
        if all([cell == symbol for cell in board[i]]) or all([board[j][i] == symbol for j in range(3)]):
            return True
    return board[0][0] == board[1][1] == board[2][2] == symbol or \
           board[0][2] == board[1][1] == board[2][0] == symbol

def is_board_full():
    return all(cell != '' for row in board for cell in row)

def handle_moves(x, y, symbol):
    global game_over, game_started
    if game_over or not game_started:
        print("Game has not started or has ended. Waiting for players to reconnect.")
        return
    if board[x][y] == '':
        board[x][y] = symbol
        print_board()
        time.sleep(1)
        if is_winner(symbol):
            end_game(f"Player {symbol} wins!")
        elif is_board_full():
            end_game("It's a tie!")
        else:
            next_turn = 'O' if symbol == 'X' else 'X'
            print(f"It's Player {next_turn}'s turn!")
            sync_pub.publish(SyncMessage(symbol=next_turn))
            board_status_pub.publish(BoardStatusMessage(board=board))
    else:
        print(f"Invalid move by Player {symbol} at ({x}, {y}). Requesting another move.")
        sync_pub.publish(SyncMessage(symbol=symbol))
        board_status_pub.publish(BoardStatusMessage(board=board))

def print_board():
    for row in board:
        print("|".join([' ' + cell + ' ' for cell in row]))
        print("-" * 9)

def reset_board():
    global board, connected_players, game_over, game_started
    board = [['', '', ''], ['', '', ''], ['', '', '']]
    connected_players = set()
    game_over = False
    game_started = False

def end_game(message):
    global game_over
    print(message)
    gameover_pub.publish(GameOverMessage(game_over=True, message=message))
    game_over = True
    print("To restart the game, both players need to reconnect.")
    reset_board()

def on_player_connect(msg: PlayerConnectMessage):
    global connected_players, game_started
    connected_players.add(msg.player)
    print(f"Player {msg.player} is connected!")
    if len(connected_players) == 2:
        print("Both players are connected!")
        time.sleep(2)
        start_game()

def on_moves(msg: MovesMessage):
    handle_moves(msg.x, msg.y, msg.symbol)

def start_game():
    print('The Game Tic-Tac-Toe is Starting')
    global game_started
    game_started = True
    time.sleep(1)
    starting_player = random.choice([1, 2])
    starting_symbol = 'X' if starting_player == 1 else 'O'
    print(f"Player {starting_player} ('{starting_symbol}') starts!")
    sync_pub.publish(SyncMessage(symbol=starting_symbol))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        broker = 'redis'
        print('Using redis broker')
    else:
        broker = str(sys.argv[1])
        print('Using defualt broker')
    if broker == 'redis':
        from commlib.transports.redis import ConnectionParameters
        transport = TransportType.REDIS
        print('Using redis broker')
    elif broker == 'amqp':
        from commlib.transports.amqp import ConnectionParameters
        transport = TransportType.AMQP
        print('Using amqp broker')
    elif broker == 'mqtt':
        from commlib.transports.mqtt import ConnectionParameters
        transport = TransportType.MQTT
        print('Using mqtt broker')
    else:
        print('Not a valid broker-type was given!')
        sys.exit(1)
    conn_params = ConnectionParameters()
    try:

        # Create Node
        node = Node(node_name='board',
                    transport_connection_params=conn_params,
                    debug=True)

        # Create Subscribers and Publishers
        moves_sub = node.create_subscriber(msg_type=MovesMessage,
                                           topic='moves',
                                           on_message=on_moves)
        player_connect_sub = node.create_subscriber(msg_type=PlayerConnectMessage,
                                                    topic='player_connect',
                                                    on_message=on_player_connect)
        sync_pub = node.create_publisher(msg_type=SyncMessage,
                                         topic='sync')
        gameover_pub = node.create_publisher(msg_type=GameOverMessage,
                                     topic='gameover')

        print('Node initialized and subscribers/publishers created.')

        # Create a publisher for BoardStatusMessage
        board_status_pub = node.create_publisher(msg_type=BoardStatusMessage,
                                         topic='board_status')

        node.run_forever(sleep_rate=2)
            
    except KeyboardInterrupt:
        print("\nGame terminated by the user.")
    except Exception as e:
        print(f"Failed to establish a connection: {e}")
