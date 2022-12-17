import Client
import Graphics


class ClientGraphicsInterface:
    """Connects GUI to Client"""
    def __init__(self):
        """Sets relationship between Graphics Updater and Client"""
        self.client = Client.Client()
        self.updater = Graphics.GraphicsUpdater(self.client)
        self.client.set_observer(self.updater)
        self.client.gameLoop()


if __name__ == '__main__':
    ClientGraphicsInterface()
