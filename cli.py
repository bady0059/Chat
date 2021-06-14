import socket, sys, threading, tkinter as tk, time, queue
from datetime import date

PORT = 1058
HOST = 'localhost'
messageToSend = queue.Queue()  # queue of massages to send


class ClientListener(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = HOST, PORT
        self.socket.connect(address)
        while True:
            if not messageToSend.empty():
                name = messageToSend.get()
                self.socket.send(name.encode())

            data = self.socket.recv(1024).decode("utf-8")
            if data != "":
                if data[0] == "0":
                    GuiThread.clear_users()
                    for name in data.split('0 '):
                        if name != "":
                            GuiThread.add_user(name)
                elif data[0] == "1":
                    if "==>" in data:
                        GuiThread.write(data[2:], "red")
                    else:
                        GuiThread.write(data[2:], "black")
                elif data[0] == "5":
                    GuiThread.write(data[2:], "blue")

# the main window chat
class Gui(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    # exit
    def exitClick(self, event):
        clientListenerThread.socket.close()
        exit(0)

    # get massage and color and print them the text box
    def write(self, text, color):
        self.chat.configure(state="normal")
        self.chat.insert(tk.END, text + '\n', color)
        self.chat.configure(state="disabled")

    # send message
    def sendMessageClick(self, num_command, textField):
        message = num_command + " " + textField.get()
        if num_command == "5":
            for i in self.usersPanel.curselection():
                name = self.usersPanel.get(i)
            message = num_command + " " + name + " " + textField.get()
        clientListenerThread.socket.send(message.encode("utf-8"))
        textField.delete(0, "end")  # clears textField

    # add user the list
    def add_user(self, name):
        self.usersPanel.insert("end", name)

    # clear users form list
    def clear_users(self):
        self.usersPanel.delete(0, 'end')

    def sendCommand(self, num_command):
        name = ""
        for i in self.usersPanel.curselection():
            name = self.usersPanel.get(i)
        clientListenerThread.socket.send(str(num_command + " " + name).encode("utf-8"))

    # the gui window
    def run(self):
        self.root = tk.Tk()
        self.root.title("Chat")
        self.root.minsize(600, 400)

        mainFrame = tk.Frame(self.root)
        mainFrame.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E)

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # ChatField
        self.chat = tk.Text(mainFrame)
        self.chat.configure(state="disabled")
        self.chat.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.chat.tag_config('red', foreground="red")
        self.chat.tag_config('black', foreground="black")
        self.chat.tag_config('blue',  foreground="blue")

        # TextFieldToSend
        textField = tk.Entry(mainFrame)
        textField.grid(column=0, row=1, sticky=tk.N + tk.S + tk.W + tk.E)

        # usersPanel
        self.usersPanel = tk.Listbox(mainFrame)
        self.usersPanel.grid(column=2, row=0, sticky=tk.N + tk.S + tk.W + tk.E)

        # SendMessageButton
        buttonSend = tk.Button(mainFrame)
        buttonSend["text"] = "Send Message"
        buttonSend.grid(column=0, row=2, sticky=tk.N + tk.S + tk.W + tk.E)
        buttonSend.bind("<Button-1>", lambda event: self.sendMessageClick("1", textField))

        # kickButton
        buttonKick = tk.Button(mainFrame)
        buttonKick["text"] = "Kick"
        buttonKick.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W + tk.E)
        buttonKick.bind("<Button-1>", lambda event: self.sendCommand("3"))

        # muteButton
        buttonMute = tk.Button(mainFrame)
        buttonMute["text"] = "Mute"
        buttonMute.grid(column=1, row=2, sticky=tk.N + tk.S + tk.W + tk.E)
        buttonMute.bind("<Button-1>", lambda event: self.sendCommand("4"))

        # SendPrivateMessageButton
        buttonPrivate = tk.Button(mainFrame)
        buttonPrivate["text"] = "Send private message"
        buttonPrivate.grid(column=2, row=1, sticky=tk.N + tk.S + tk.W + tk.E)
        buttonPrivate.bind("<Button-1>", lambda event: self.sendMessageClick("5", textField))

        # ExitButton
        buttonExit = tk.Button(mainFrame)
        buttonExit["text"] = "Exit"
        buttonExit["background"] = "gray"
        buttonExit.grid(column=2, row=2, sticky=tk.N + tk.S + tk.W + tk.E)
        buttonExit.bind("<Button-1>", self.exitClick)

        self.root.mainloop()

# the first window of get the user name
class getUsername(threading.Thread):
    def __init__(self):
        window = tk.Tk()
        window.title = ("Log-In")
        usernametext = tk.Label(window, text="Username")
        usernameguess = tk.Entry(window)
        loginButton = tk.Button(text="Login")
        loginButton.bind("<Button-1>", lambda event: self.loginClick(event, usernameguess, window))
        usernametext.pack()
        usernameguess.pack()
        loginButton.pack()
        window.mainloop()

    def loginClick(self, event, usernameguess, window):
        message = "0 "
        message += usernameguess.get()
        messageToSend.put(message)
        window.destroy()


getUsr = getUsername()
GuiThread = Gui()
GuiThread.start()
clientListenerThread = ClientListener()
clientListenerThread.daemon = True
clientListenerThread.start()
