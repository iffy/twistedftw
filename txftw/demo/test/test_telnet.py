from twisted.trial.unittest import TestCase
from twisted.test.proto_helpers import StringTransport

from mock import create_autospec

from txftw.demo import message
from txftw.demo.room import Building, Room
from txftw.demo.telnet import DemoFactory, DemoProtocol


class DemoFactoryTest(TestCase):


    def test_init(self):
        """
        The factory should know about a Building.
        """
        f = DemoFactory('building')
        self.assertEqual(f.building, 'building')


    def test_buildProtocol(self):
        """
        Should let the protocol know about the factory
        """
        f = DemoFactory('building')
        proto = f.buildProtocol(None)
        self.assertTrue(isinstance(proto, DemoProtocol))
        self.assertEqual(proto.factory, f)



class DemoProtocolTest(TestCase):


    def proto(self):
        """
        Return a protocol connected to a StringTransport
        """
        proto = DemoProtocol()
        transport = StringTransport()
        proto.makeConnection(transport)
        transport.clear()

        return proto


    def test_connectionMade(self):
        proto = DemoProtocol()
        transport = StringTransport()
        proto.makeConnection(transport)
        self.assertNotEqual(transport.value(), '',
                            "Should write some instructions")


    def test_init_lineReceived(self):
        """
        If the protocol is in the init state and a line is received, it is a
        room key.
        """
        building = Building()
        factory = DemoFactory(building)

        proto = factory.buildProtocol(None)
        transport = StringTransport()
        proto.makeConnection(transport)
        transport.clear()
        
        # try a bad key
        proto.lineReceived('foo')
        self.assertNotEqual(transport.value(), '')
        transport.clear()

        # try a good key
        key = building.createRoom()
        proto.lineReceived(key)
        self.assertNotEqual(transport.value(), '', "Should ack a good key")
        room = building.getRoom(key)
        self.assertEqual(list(room.contents().values())[0], proto,
                         "Should have added the protocol to the room")


    def test_setRoom(self):
        """
        Should set the room and name of the connection.
        """
        proto = DemoProtocol()
        transport = StringTransport()
        proto.makeConnection(transport)
        transport.clear()

        room = Room()
        proto.setRoom(room, 'bob')
        self.assertEqual(proto.room, room)
        self.assertEqual(proto.name, 'bob')
        self.assertIn('bob', transport.value(), "Should include the name "
                      "in a message to the client")


    def test_setRoom_None_quit(self):
        """
        If room is set to None, close the connection
        """
        proto = self.proto()
        proto.transport.loseConnection = create_autospec(
                            proto.transport.loseConnection)

        proto.setRoom(None, 'bob')
        proto.transport.loseConnection.assert_called_once_with()


    def test_messageReceived_msg(self):
        """
        Messages should be printed out
        """
        proto = self.proto()

        proto.messageReceived(message.msg('hello', 'user'))
        self.assertEqual(proto.transport.value(), 'user: hello\r\n')


    def test_messageReceived_leave(self):
        """
        Leaving should be printed out
        """
        proto = self.proto()
        proto.messageReceived(message.leave('user'))
        self.assertIn('user', proto.transport.value(), "Should indicate that "
                      "the user left")


    def test_messageReceived_enter(self):
        """
        Entering should be printed out
        """
        proto = self.proto()
        proto.messageReceived(message.enter('user'))
        self.assertIn('user', proto.transport.value(), "Should indicate that "
                      "the user entered")


    def test_connectionLost(self):
        """
        If the client closes the connection, leave the room
        """
        proto = self.proto()
        room = Room()
        room.enter('bob', proto)

        proto.connectionLost(None)
        self.assertEqual(len(room.contents()), 0, "Should not be in the room "
                         "anymore")


    def test_connectionLost_noRoom(self):
        """
        If the client closes the connection when not in a room, it should not
        cause a problem.
        """
        proto = self.proto()
        proto.connectionLost(None)


    def test_lineReceived_inRoom(self):
        """
        If a line is received when the protocol is in a room, it should be
        turned into a message.
        """
        proto = self.proto()
        room = Room()
        room.enter('bob', proto)

        proto.transport.clear()
        proto.messageReceived = create_autospec(proto.messageReceived)

        proto.lineReceived('Hey guys')
        proto.messageReceived.assert_called_once_with(
                message.msg('Hey guys', 'bob'))





