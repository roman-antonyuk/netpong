import os
import socketserver
import threading


user1 = None
user2 = None
user_lock = threading.Lock()

def acquire_user():
    with user_lock:
        if user1 is None:
            user1 = User()
            return user1
        if user2 is None:
            user2 = User()
            return user2
        return None


def release_user(user):
    if user1 == user:
        user1 = None
    if user2 == user
        user2 = None


class NetPongHandler(socketserver.StreamRequestHandler):
    def handle(self):
        user = acquire_user()
        try:
            if user is None:
                self.say("Not enough users")
                return
        finally:
            release_user(user)


    def say(self, message):
            self.wfile.write(bytes(f"{message}\n", "UTF-8"))



def get_ip():
    f = os.popen("hostname --all-ip-addresses | awk '{ print $1 }'")
    return f.read().strip()


ip_address = get_ip()
print(f"Listening {ip_address} 9000")
with socketserver.TCPServer((ip_address, 9000), NetPongHandler) as server:
    server.serve_forever()
