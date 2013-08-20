from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineOnlyReceiver


from txftw.demo import message



class DemoProtocol(LineOnlyReceiver):

    delimiter = '\r\n'

    room = None
    name = ''


    def connectionMade(self):
        self.sendLine("Enter the key, then press enter")


    def connectionLost(self, reason):
        if self.room:
            self.room.leave(self.name)


    def lineReceived(self, line):
        if self.room:
            return self._handleMessage(line)
        else:
            return self._handleRoomKey(line)


    def _handleMessage(self, line):
        self.room.broadcast(message.msg(line, self.name))


    def _handleRoomKey(self, line):
        try:
            room = self.factory.building.getRoom(line)
            self.sendLine("Welcome!")
            room.enter('telnet', self)
        except KeyError:
            self.sendLine("Unknown key %r.  Try again." % (line,))


    def setRoom(self, room, name):
        if not room:
            self.room = None
            self.sendLine('You are being disconnected.  Bye, bye.')
            self.transport.loseConnection()
            return
        self.room = room
        self.name = name
        self.sendLine('You are %s' % (name,))


    def messageReceived(self, msg):
        if msg['event'] == 'leave':
            self.sendLine(' (%s left)' % (msg['who'],))
        elif msg['event'] == 'enter':
            self.sendLine(' (%s entered)' % (msg['who'],))
        elif msg['event'] == 'msg':
            self.sendLine('%s: %s' % (msg['who'], msg['msg']))



class DemoFactory(Factory):


    protocol = DemoProtocol

    
    def __init__(self, building):
        self.building = building


