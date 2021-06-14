import socket, sys, threading, queue, time
from datetime import datetime
import traceback

PORT = 1058
HOST = 'localhost'
users = []  # save all users in list


# user class
class User:
    def __init__(self, name, conn):
        self.name = name  # name of user
        self.muted = False
        self.conn = conn  # the connection


# server class
class Server:

    # start socket
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            address = HOST, PORT
            self.server.bind(address)
        except socket.error:
            return
        self.server.listen()

    # close the socket
    def exit(self):
        self.server.close()

    # get new connection and create thread for him
    def run(self):
        while True:
            conn, addr = self.server.accept()
            threading.Thread(target=self.handleUser, args=(conn,)).start()

    # handle the user
    def handleUser(self, conn):
        user = User(conn.recv(1024).decode("utf-8")[2:], conn)  # get his name and create object
        users.append(user)  # add him the new user to the list of users
        self.broadcast(user.name + " has joined the chat")

        try:
            while True:
                message = conn.recv(1024).decode("utf-8")
                if not user.muted:
                    if message != "":
                        if message[0] == "1":  # send massage for all
                            self.broadcast(message[2:], user.name)
                        elif message[0] == "3":  # kick other user
                            self.kick_user(message[2:])
                        elif message[0] == "4":  # muted other user
                            self.mute_user(message[2:])
                        elif message[0] == "5":  # send private massage
                            self.send_private(user, message[2:])

                # update the list of users
                for u in users:
                    print(user.name)
                    conn.send(("0 " + u.name).encode("utf-8"))

                time.sleep(1)
        except Exception:  # user exited
            users.remove(user)
            self.broadcast(user.name + " has exited the chat")

    # kick user
    def kick_user(self, name):
        for u in users:
            if name == u.name:
                self.broadcast(u.name + " has kicked from the chat")
                users.remove(u)
                u.conn.close()

    # muted user
    def mute_user(self, name):
        for u in users:
            if name == u.name:
                self.broadcast(u.name + " has muted")
                u.muted = True

    # send private massage
    def send_private(self, user, message):
        now = datetime.now().strftime("%H:%M")
        print(message.split(" "))
        receiver_name = message.split(" ")[0]
        message = message.split(" ")[1]

        for u in users:
            if receiver_name == u.name:
                message = str("5 " + now + " " + user.name + " -> " + message)
                u.conn.send(message.encode("utf-8"))
                user.conn.send(message.encode("utf-8"))

    # send massage for all users
    def broadcast(self, message, name=""):
        now = datetime.now().strftime("%H:%M")
        for user in users:
            if name != "":
                user.conn.send(str("1 " + now + " " + name + " -> " + message).encode("utf-8"))
            else:
                user.conn.send(str("1 " + now + " ==> " + message).encode("utf-8"))


newServer = Server()
newServer.run()
Server.exit()
