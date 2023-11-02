import random
import time
import sys

from commlib.msg import PubSubMessage, RPCMessage
from commlib.node import Node, TransportType

PLAYER_SYMBOL = 'O'
game_over = False
current_board = [['', '', ''], ['', '', ''], ['', '', '']]

# Add new message class
class BoardStatusMessage(PubSubMessage):
    board: list[list[str]]

class MovesMessage(PubSubMessage):
    x: int
    y: int
    symbol: str

class SyncMessage(PubSubMessage):
    symbol: str

class PlayerConnectMessage(PubSubMessage):
    player: str 

class GameOverMessage(PubSubMessage):
    game_over: bool
    message: str

# Add a function to handle board status messages
def on_board_status(msg: BoardStatusMessage):
    global current_board
    current_board = msg.board


def make_move():
    empty_cells = [(i, j) for i in range(3) for j in range(3) if current_board[i][j] == '']
    if empty_cells:
        i, j = random.choice(empty_cells)
        current_board[i][j] = PLAYER_SYMBOL
        print(f"Making a move at ({i}, {j}) with symbol {PLAYER_SYMBOL}")
        time.sleep(1)
        move_msg = MovesMessage(x=i, y=j, symbol=PLAYER_SYMBOL)
        moves_pub.publish(move_msg)
    else:
        print("No empty cells found!")

def on_sync(msg):
    if msg.symbol == PLAYER_SYMBOL:
        make_move()

def on_gameover(msg: GameOverMessage):
    global game_over
    print(msg.message)
    game_over = msg.game_over
    if game_over:
        reconnect()

def reconnect():
    global game_over, current_board
    game_over = False
    current_board = [['', '', ''], ['', '', ''], ['', '', '']]
    print("Reconnecting...")
    time.sleep(2)
    player_connect_msg = PlayerConnectMessage(player=PLAYER_SYMBOL)
    player_connect_pub.publish(player_connect_msg) 
    print("Player connect message published.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        broker = 'redis'
    else:
        broker = str(sys.argv[1])
    if broker == 'redis':
        from commlib.transports.redis import ConnectionParameters
        transport = TransportType.REDIS
    elif broker == 'amqp':
        from commlib.transports.amqp import ConnectionParameters
        transport = TransportType.AMQP
    elif broker == 'mqtt':
        from commlib.transports.mqtt import ConnectionParameters
        transport = TransportType.MQTT
    else:
        print('Not a valid broker-type was given!')
        sys.exit(1)
    conn_params = ConnectionParameters(host='redis')
    try:

        # Create Node
        node = Node(node_name='player2',
                    transport_connection_params=conn_params,
                    debug=True)

        # Create Subscribers and Publishers
        sync_sub = node.create_subscriber(msg_type=SyncMessage,
                                          topic='sync',
                                          on_message=on_sync)
        gameover_sub = node.create_subscriber(msg_type=GameOverMessage,
                                              topic='gameover',
                                              on_message=on_gameover)
        moves_pub = node.create_publisher(msg_type=MovesMessage,
                                          topic='moves')
        print("Publishing player connect message...")
        player_connect_pub = node.create_publisher(msg_type=PlayerConnectMessage,
                                                   topic='player_connect')
        print('Node initialized and subscribers/publishers created.')

        # Send player connection message
        player_connect_msg = PlayerConnectMessage(player=PLAYER_SYMBOL)
        player_connect_pub.publish(player_connect_msg) 
        print("Player connect message published.")
        
        # Create a subscriber for BoardStatusMessage
        board_status_sub = node.create_subscriber(msg_type=BoardStatusMessage,
                                                topic='board_status',
                                                on_message=on_board_status)

        node.run_forever(sleep_rate=2)

    except KeyboardInterrupt:
        print("\nGame terminated by the user.")
    except Exception as e:
        print(f"Failed to establish a connection: {e}")
