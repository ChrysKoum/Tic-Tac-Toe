# Tic Tac Toe Game

This project is a distributed Tic Tac Toe game implemented using Python, RabbitMQ, Redis, Docker, and more. The game consists of two automated players and a board, all communicating through message brokers.

## Prerequisites

- Python
- RabbitMQ
- Redis
- Docker
- commlib-py
- Paho MQTT

## Installation

### Dependencies

Install the necessary dependencies:

```bash
# RabbitMQ
sudo systemctl start rabbitmq-server
sudo rabbitmq-plugins enable rabbitmq_management
sudo systemctl status rabbitmq

# Redis
sudo systemctl start redis
sudo systemctl status redis
```

### Docker Setup

Without using Docker Compose, you need to build the images and containers as follows:

#### Build Images

```bash
docker build -t tictactoe-board -f Dockerfile.board .
docker build -t tictactoe-player1 -f Dockerfile.player1 .
docker build -t tictactoe-player2 -f Dockerfile.player2 .
```

#### Build Network

```bash
docker network create tictactoe-network
```

#### Build Containers

```bash
docker run --name redis --network tictactoe-network -d redis
docker run -it --name board --network tictactoe-network tictactoe-board
docker run --name player1 --network tictactoe-network -d tictactoe-player1
docker run --name player2 --network tictactoe-network -d tictactoe-player2
```

### Docker Compose

To run all together:

```bash
docker-compose up
```

To stop:

```bash
docker-compose down
```

## Brokers

### commlib-py

Download and set up `commlib-py`.

### Deploy a Broker

Deploy an MQTT/AMQP broker (RabbitMQ, Redis).

## Game Implementation

- I Implement a basic Tic Tac Toe game.
- I Create one Python script for each player and one for the board/master.
- The players synchronize and play autonomously.
- I Used pub-sub to send/receive player's commands.

## Dockerization

- I Dockerize the Tic Tac Toe scripts (3 images).
- I Deployed them using Docker and ensure the game works as expected.
- I Dockerize everything using Docker Compose.

## Unix Services

- I deploy the three scripts as services in Unix.
- I Used `systemctl` to manage them and `journalctl` to see the logs.

## Model-Driven Engineering (MDE)

- I Create a simple DSL for computations (e.g., 1 PLUS 2 -> 1+2).
- Used `textx` to define the metamodel and grammar.
- I Interpret the model and print the results using Python.
- I Generate Python code to print each result using Jinja templates.

## Author
- Chrysostomos Koumides
