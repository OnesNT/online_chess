from socket import *
import threading


class Queue:
    """Provides data that the Server uses to manage games and clients"""

    def __init__(self):
        """Initialize needed Queues and vars"""
        # Maps user to cookie    {username: cookie}
        self.userMap = {}
        # dict of people waiting for game {cookie: desiredOpponentCookie}
        self.waiting = {}
        # dict of ongoing games    {cookie : opCookie}
        self.game = {}
        # Maps cookie to user    {cookie: user}
        self.cookieMap = {}
        # maps cookie to socket designated for receiving data
        self.cookieReceiver = {}
        # Keeps track of number of users, cookies based off of this
        self.users = 0


class Server:
    """Communicates to Clients"""

    def __init__(self, address='0.0.0.0', port_number=4000, connections=10):
        """Binds to address:port, creates a Queue object, and threads off incoming connections.
         Handles up to connections/2 clients,
        as each client requires 2 socket connections
        :param address: str
        :param port_number: int
        :param connections: int"""

        identifier = (address, port_number)

        # Create and bind server socket.
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(identifier)

        self.server_socket.listen(connections)

        self.q = Queue()

        while True:
            connection_socket, client_address = self.server_socket.accept()
            thread = threading.Thread(target=self.handle_client, args=(connection_socket,))
            thread.start()

    def reply(self, socket, msg=''):
        """Sends message to socket
        :param socket: socket
        :param msg: str"""
        reply = msg.encode()
        socket.send(reply)

    def handle_client(self, connection_socket):
        """Awaits Client Commands, sends info to clients and keeps track of what clients are in each game
        :param connection_socket: socket"""
        print('Handling Client!')
        running = True
        while running:
            try:
                # Messages will be received in the form:
                # User: Cookie: Command: Data
                # Split into parts
                message_from_client = connection_socket.recv(2048)
                msg = message_from_client.decode()
                user = msg[0: msg.index(':')]
                msg = msg[msg.index(':') + 2:]
                cookie = msg[0: msg.index(':')]
                msg = msg[msg.index(':') + 2:]
                command = msg[0: msg.index(':')]
                msg = msg[msg.index(':') + 2:]
                data = msg

                # Check for known commands
                if command == "SetRecv":
                    self.q.cookieReceiver[cookie] = connection_socket
                    # Messages destined to the client with this cookie go through this socket
                    print('set receiver at cookie', cookie)

                # if username exists
                if user in self.q.userMap:
                    # and does not match cookie
                    if self.q.userMap[user] != cookie:
                        error = "ERR: Username already exists!"
                        reply = error.encode()
                        connection_socket.send(reply)
                    else:
                        # client searching for game
                        if command == 'Start':
                            self.reply(connection_socket, 'None')
                            found = False
                            # no specified opponent
                            if data == 'None':
                                for userCookie in self.q.waiting:
                                    if self.q.waiting[userCookie] == 'None' or self.q.waiting[userCookie] == user:
                                        # link waiting opponents to new client
                                        self.q.game[cookie] = userCookie
                                        self.q.game[userCookie] = cookie
                                        try:
                                            self.reply(self.q.cookieReceiver[cookie], str("StartB" + userCookie))
                                            self.reply(self.q.cookieReceiver[userCookie], (str("StartW" + cookie)))
                                        except Exception as e:
                                            print(e)
                                        found = True
                                        # remove client from waiting queue
                                        del self.q.waiting[userCookie]
                                        break
                            else:
                                # find chosen opponent
                                if data in self.q.userMap:  # username to cookie
                                    if self.q.userMap[data] in self.q.waiting and \
                                            (self.q.waiting[self.q.userMap[data]] == user or
                                             self.q.waiting[self.q.userMap[data]] == 'None'):
                                        # self.q.userMap[data] is opponent cookie
                                        self.q.game[cookie] = self.q.userMap[data]
                                        self.q.game[self.q.userMap[data]] = cookie
                                        try:
                                            self.reply \
                                                (self.q.cookieReceiver[cookie], str("StartB" + self.q.userMap[data]))
                                            self.reply \
                                                (self.q.cookieReceiver[self.q.userMap[data]], (str("StartW" + cookie)))
                                        except Exception as e:
                                            print(e)
                                        found = True
                                        # remove client from waiting queue
                                        del self.q.waiting[self.q.userMap[data]]
                            # add client to waiting queue if no opponent found
                            if not found:
                                self.q.waiting[cookie] = data
                            self.q.cookieMap[cookie] = user
                            self.reply(connection_socket, "No")
                        # lookup name given cookie
                        if command == 'GetName':
                            reply = 'None'
                            if data in self.q.cookieMap:
                                reply = self.q.cookieMap[data]
                            self.reply(connection_socket, reply)
                        # Move Format: P#xy  where c is color, P is piece,
                        # P is piece num, x is 0-7, y is 0-7 -- use # = 0 for singular pieces(Q, K)
                        if command == 'Move':
                            reply = 'OK'
                            self.reply(connection_socket, reply)
                            # forward data to opponent
                            self.reply(self.q.cookieReceiver[self.q.game[cookie]], (str("Move" + data)))
                        if command == 'Prom':  # Promote Format: P#a1V    where V is value
                            reply = 'OK'
                            self.reply(connection_socket, reply)
                            # forward data to opponent
                            self.reply(self.q.cookieReceiver[self.q.game[cookie]], (str("Prom" + data)))
                        if command == 'Chat':
                            reply = 'OK'
                            self.reply(connection_socket, reply)
                            # forward data to opponent
                            self.reply(self.q.cookieReceiver[self.q.game[cookie]], (str("Chat" + data)))
                        if command == 'End':
                            if data != 'None':
                                reply = "End: Closing Connection"
                                self.reply(connection_socket, reply)
                                if cookie in self.q.game:
                                    self.reply(self.q.cookieReceiver[self.q.game[cookie]], (str("End" + data)))
                                    if self.q.cookieMap[self.q.game[cookie]] in self.q.userMap:
                                        # Free up oponents username
                                        del self.q.userMap[self.q.cookieMap[self.q.game[cookie]]]
                                # Remove from Queue
                                if cookie in self.q.waiting:
                                    del self.q.waiting[cookie]
                                # Remove username association
                                if user in self.q.userMap:
                                    del self.q.userMap[user]
                                running = False
                                # close socket
                                connection_socket.close()
                                reply = 'None'
                                self.reply(connection_socket, reply)
                else:
                    # Client asking for cookie
                    if command == 'Cookie':
                        self.q.users += 1
                        reply = str(self.q.users)
                        self.reply(connection_socket, reply)
                    # Client wants to be assigned a name
                    if command == 'User':
                        if user == 'None':
                            reply = "ERR: Invalid Name!"
                            self.reply(connection_socket, reply)
                        else:
                            self.q.userMap[user] = cookie
                            reply = "OK"
                            self.reply(connection_socket, reply)

                print(user, cookie, command, data)
            except Exception as e:
                pass


Server()
