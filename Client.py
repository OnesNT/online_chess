from socket import *
import threading


class Client:
    """Handles communicating with server and passing messages to the GUI"""

    def __init__(self):
        """Initializes variables and defaults"""
        self.default_ip = 'localhost'
        self.default_port = 4000
        self.connected_ip = 'localhost'
        self.connected_port = 4000
        self.server_identifier = (self.default_ip, self.default_port)
        self.cookie = 0
        self.username = ''
        self.endGame = False
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.recv_socket = socket(AF_INET, SOCK_STREAM)
        self.observer = None
        self.connected = False
        self.ready = False
        self.setReceiver = False
        self.running = True

        self.queue = {'Start': '', 'Chat': '', 'Move': '', 'Prom': '', 'End': ''}

    def comm(self, user='', cook='None', command='Cookie', data='None'):
        """Sends messages to server in expected format
        :param user: str
        :param cook: int
        :param command: str
        :param data: str
        :return reply: str"""
        if not self.connected:
            self.client_socket.settimeout(1)
            try:
                self.client_socket.connect(self.server_identifier)
                self.recv_socket.connect(self.server_identifier)
                self.connected = True
            # Handled by window prompting the user
            except TimeoutError:
                # Reset connections
                self.client_socket = socket(AF_INET, SOCK_STREAM)
                self.recv_socket = socket(AF_INET, SOCK_STREAM)
                self.connected = False

        if self.cookie != 0 and not self.setReceiver:
            # Links Receiving socket to Cookie
            self.recv_socket.send((self.username + ": " + str(self.cookie) + ': ' + 'SetRecv' + ': ' + "None").encode())
            self.setReceiver = True

        # Send commands
        if self.connected and not self.endGame:
            if user == '':
                user = self.username
            if cook == 'None':
                cook = self.cookie
            message = user + ": " + str(cook) + ': ' + command + ': ' + data
            message = message.encode()
            self.client_socket.send(message)
            reply = self.client_socket.recv(2048)
            reply = reply.decode()
            return reply
        return ''

    def setUName(self):
        """Set username, returns server reply
        :return reply: str"""
        reply = self.comm(user=self.username, cook=str(self.cookie), command='User')
        return reply

    def set_observer(self, observer):
        """Set observer to update when a message is received
        :param observer: GraphicsUpdater"""
        self.observer = observer

    def sendChat(self, msg):
        """Sends chat message to server
        :param msg: str"""
        self.comm(command='Chat', data=str(msg))

    def sendMove(self, move):
        """Sends move message to server
        :param move: str"""
        self.comm(command='Move', data=move)

    def sendProm(self, prom):
        """Sends promotion message to server
        :param prom: str"""
        self.comm(command='Prom', data=prom)

    def loop(self):
        """Listens to incoming messages until the game ends, adds them to corresponding queue"""
        while self.running:
            while self.ready and not self.endGame:
                reply = self.recv_socket.recv(2048)
                reply = reply.decode()
                print(reply)
                if reply.find('Start') == 0:
                    self.queue['Start'] = reply[reply.index("Start") + 5:]
                elif reply.find('Chat') == 0:
                    self.queue['Chat'] = reply[reply.index("Chat") + 4:]
                elif reply.find('Prom') == 0:
                    self.queue['Prom'] = reply[reply.index("Prom") + 4:]
                elif reply.find('Move') == 0:
                    self.queue['Move'] = reply[reply.index("Move") + 4:]
                elif reply.find('End') == 0:
                    self.queue['End'] = reply[reply.index("End") + 3:]

    def checkQueue(self):
        """Checks Queues and calls observer methods correspondingly"""
        if self.queue['Start'] != '':
            # info contains opponent cookie and side user is playing on
            info = self.queue['Start']
            self.observer.graphics.connection.destroy()
            self.observer.graphics.statusText.configure(text='Game against ' +
                                                             self.comm(command='GetName', data=info[1:]))
            if info[0] == 'W':
                self.observer.side = 'white'
                self.observer.otherSide = 'black'
            else:
                self.observer.side = 'black'
                self.observer.otherSide = 'white'
            self.observer.setBoard()
            self.queue['Start'] = ''

        if self.queue['Chat'] != '':
            info = self.queue['Chat']
            self.observer.MsgReceive(info)
            self.queue['Chat'] = ''

        if self.queue['Move'] != '':
            info = self.queue['Move']
            pieceName = info[0: 2]
            moveTo = [int(info[2]), int(info[3])]
            if self.observer.side == 'white':
                self.observer.board.move(self.observer.board.black[pieceName], moveTo)
                self.observer.setBoard()
                self.observer.nextMove = 'white'
            if self.observer.side == 'black':
                self.observer.board.move(self.observer.board.white[pieceName], moveTo)
                self.observer.setBoard()
                self.observer.nextMove = 'black'
            self.queue['Move'] = ''

        if self.queue['Prom'] != '':
            info = self.queue['Prom']
            pieceName = info[0:2]
            newValue = info[2]
            if self.observer.side == 'white':
                self.observer.board.promote(self.observer.board.black[pieceName], newValue)
                self.observer.setBoard()
                self.observer.nextMove = 'white'
            if self.observer.side == 'black':
                self.observer.board.promote(self.observer.board.white[pieceName], newValue)
                self.observer.setBoard()
                self.observer.nextMove = 'black'
            self.queue['Prom'] = ''

        if self.queue['End'] != '':
            info = self.queue['End']
            self.observer.endScreen(info)
            self.queue['End'] = ''

    def gameLoop(self):
        """Loop which runs both GUI and Server communication"""
        # Thread for consistent listening for messages without blocking
        thread = threading.Thread(target=self.loop, daemon=True)
        thread.start()
        while not self.endGame:
            self.checkQueue()
            self.observer.update()
