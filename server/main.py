import os
import sys
import socketserver
import threading
import pygame
import json


SERVER_PORT=9000
MOVE_UP = 1
MOVE_DOWN = -1
PADDLE_STEP = 10

STATUS_NEW = "NEW"
STATUS_PLAYING = "PLAYING"
STATUS_GAMEOVER = "GAMEOVER"


class NullPlayer:
    def __init__(self):
        self.is_ready = False
        self.paddle_pos = 0
        self.paddle_size = 250
        self.score = 0

    def move_paddle(self, direction):
        pass

NULL_PLAYER = NullPlayer()

class Player:
    def __init__(self):
        self.is_ready = False
        self.paddle_pos = 0
        self.paddle_size = 250
        self.score = 0

    def move_paddle(self, direction):
        self.paddle_pos += direction * PADDLE_STEP


class Ball:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 3
        self.vy = 4

    def move(self):
        self.x += self.vx
        self.y += self.vy


class Game:
    def __init__(self):
        self.status = STATUS_NEW
        self.player1 = NULL_PLAYER
        self.player2 = NULL_PLAYER
        self.ball = Ball()

    def acquire_player(self):
        player_lock = threading.Lock()
        with player_lock:
            if self.player1 == NULL_PLAYER:
                self.player1 = Player()
                return self.player1
            if self.player2 == NULL_PLAYER:
                self.player2 = Player()
                return self.player2
            return None

    def release_player(self, player):
        if self.player1 == player:
            self.player1 = NULL_PLAYER
        if self.player2 == player:
            self.player2 = NULL_PLAYER
        self.status = STATUS_NEW

    def ready(self, player):
        player.is_ready = True
        if self.player1.is_ready and self.player2.is_ready and self.status == STATUS_NEW:
            print("Start playing")
            self.ball = Ball()
            self.player1.paddle_pos = 0
            self.player2.paddle_pos = 0
            self.status = STATUS_PLAYING

    def tick(self):
        # print("Ticking...")
        if self.status == STATUS_PLAYING:
            self.ball.move()
            print(f"Ball: {self.ball.x}, {self.ball.y}")
            if self.ball.x < 0:
                self.ball.x = -self.ball.x
                self.ball.vx *= -1
            elif self.ball.x > 1000:
                self.ball.x = 2000 - self.ball.x
                self.ball.vx *= -1
            if self.ball.y < 0:
                self.ball.y = -self.ball.y
                self.ball.vy *= -1
            elif self.ball.y > 1000:
                self.ball.y = 2000 - self.ball.y
                self.ball.vy *= -1

            # handle hit paddles
            # check if some player missed: score and go to GAMEOVER
            pass


game = Game()


class NetPongHandler(socketserver.StreamRequestHandler):
    def handle(self):
        print("Connected")
        player = game.acquire_player()
        print("Acquired player")
        if player is None:
            self.send_error("SERVER_FULL")
            return

        try:
            print("Start playing")
            self.play(player)
        finally:
            print("Release player")
            game.release_player(player)

    def send_error(self, message):
        self.say(json.dumps({
            "status": "ERROR",
            "result": {
                "message": message
            }
        }))

    def play(self, player):
        while True:
            print("Obtaining command")
            command = self.rfile.readline().strip().decode("utf-8")
            print("Command " + command)
            if command == "QUIT":
                break
            if command == "READY":
                game.ready(player)
            elif command == "STATUS":
                self.status(player)
            elif command == "UP":
                player.move_paddle(MOVE_UP)
            elif command == "DOWN":
                player.move_paddle(MOVE_DOWN)

    def say(self, message):
        self.wfile.write(bytes(f"{message}\n", "UTF-8"))

    def status(self, player):
        global game
        opponent = player == game.player1 and game.player2 or game.player1

        self.say(json.dumps({
            "status": game.status,
            "ball": {
                "x": game.ball.x,
                "y": game.ball.y,
            },
            "you": {
                "pos": player.paddle_pos,
                "score": player.score,
                "ready": player.is_ready
            },
            "opponent": {
                "pos": opponent.paddle_pos,
                "score": opponent.score,
                "ready": opponent.is_ready,
            }
        }))
        


def get_ip():
    f = os.popen("hostname --all-ip-addresses | awk '{ print $1 }'")
    return f.read().strip()



class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def listen():
    ip_address = get_ip()
    with ThreadedTCPServer((ip_address, SERVER_PORT), NetPongHandler) as server:
        server.serve_forever()


listen_thread = threading.Thread(target=listen, daemon=True)
listen_thread.start()


def game_thread_fun():
    global game

    print("Entering game thread")
    clock = pygame.time.Clock()
    while True:
        game.tick()
        clock.tick(50)


game_thread = threading.Thread(target=game_thread_fun, daemon=True)
game_thread.start()


while True:
    command = input()
    if command.strip() == "quit":
        print("Quitting...")
        sys.exit(0)

