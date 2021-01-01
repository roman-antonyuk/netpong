import json
import sys
import socket
import pygame

FPS = 60
HOR_SPEED = 12
clock = pygame.time.Clock()
pygame.init()
# screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
screen = pygame.display.set_mode((800, 600))
screen_width, screen_height = pygame.display.get_surface().get_size()
done = False

paddle_height = screen_height // 4
paddle_width = 15
paddle1_y = (screen_height - paddle_height) // 2
paddle1_x = paddle_width
paddle2_y = (screen_height - paddle_height) // 2
paddle2_x = screen_width - paddle_width
xb = screen_width // 2
yb = screen_height // 2
bspeedx = 25
bspeedy = 25
radius = 15
speed = 250


# Functions
def move(direction, y):
    if direction == 1 and y > 0:
        y -= speed
    elif direction == -1 and y < screen_height - paddle_height:
        y += speed
    return y


def moveBX(x, sx):
    x += sx
    return x


def moveBY(y, sy):
    y += sy
    return y


def ballHitX(y, sy):
    if y == 0 or y == screen_height:
        return int(sy * -1)
    return sy


def ballHitP(pos, sx, player1, player2, h):
    if pos[0] == player1[0]:
        if (player1[1] <= pos[1] <= player1[1] + h):
            return int(sx * -1)
    if pos[0] == player2[0]:
        if (player2[1] <= pos[1] <= player2[1] + h):
            return int(sx * -1)
    return sx


def drawPlayer1(x, y, l, h):
    pygame.draw.rect(screen, (255, 0, 0), (x, y - h//2, -l, h), 0)


def drawPlayer2(x, y, l, h):
    pygame.draw.rect(screen, (0, 0, 255), (x, y - h//2, l, h), 0)


def drawBall(x, y, r):
    pygame.draw.circle(screen, (0, 0, 0), (x, y), r, 0)


def winP1(xb):
    if xb >= screen_width:
        return [screen_width // 2, screen_height // 2, -25, 25]
    else:
        return False


def winP2(xb):
    if xb <= 0:
        return [screen_width // 2, screen_height // 2, 25, -25]
    else:
        return False


def move_ball():
    global xb, yb
    xb = moveBX(xb, bspeedx)
    yb = moveBY(yb, bspeedy)
    return (xb, yb)


def move_player(player, direction):
    global speed, paddle1_y, paddle2_y
    if player == 1:
        return move(direction, paddle1_y)
    else:
        return move(direction, paddle2_y)

server = None

def server_connect(ip_address, port):
    global server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((ip_address, port))
    result = json.loads(server.recv(1024))
    print(result)
    return result

def send_command(command):
    global server
    server.sendall(bytes(command + "\n", 'utf-8'))
    print('Sending command: %s' % command)

def get_status():
    global server
    send_command('STATUS')
    result = json.loads(server.recv(1024))
    print(result)
    return result

def server_disconnect():
    global server
    send_command('QUIT')
    server.close()

status = server_connect(sys.argv[1], int(sys.argv[2]))
if status['status'] == 'ERROR':
    print("Can't connect to the server")
    exit()

while not done:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            done = True

    pressed = pygame.key.get_pressed()
    screen.fill((255, 255, 255))

    status = get_status()
    if status['status'] != 'PLAYING':
        send_command('READY')
        continue
    paddle1_y = int(screen_height/2 + status['you']['pos'] * screen_height / 1000)
    paddle2_y = int(screen_height/2 + status['opponent']['pos'] * screen_height / 1000)
    xb = int(screen_width/2 - status['ball']['x'] * screen_width / 1000)
    yb = int(screen_height/2 + status['ball']['y'] * screen_height / 1000)

    if pressed[pygame.K_DOWN]:
        send_command('UP')
    if pressed[pygame.K_UP]:
        send_command('DOWN')

    drawPlayer1(paddle1_x, paddle1_y, paddle_width, paddle_height)
    drawPlayer2(paddle2_x, paddle2_y, paddle_width, paddle_height)
    drawBall(xb, yb, radius)

    pygame.display.flip()

server_disconnect()
pygame.quit()
