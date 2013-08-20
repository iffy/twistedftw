from twisted.trial.unittest import TestCase
from mock import MagicMock

from txftw.demo.room import Room, NotInRoom



class RoomTest(TestCase):


    def test_enter(self):
        """
        Things can enter a room
        """
        room = Room()
        thing = MagicMock()

        room.enter(thing)
        self.assertEqual(thing.room, room, "Should set room")
        self.assertEqual(room.contents(), [thing])


    def test_enter_twice(self):
        """
        Entering twice should raise an error.
        """
        room = Room()
        thing = MagicMock()
        
        room.enter(thing)
        self.assertRaises(Exception, room.enter, thing)


    def test_leave(self):
        """
        Things can leave a room
        """
        room = Room()
        thing = MagicMock()

        room.enter(thing)
        room.leave(thing)
        self.assertEqual(thing.room, None)
        self.assertEqual(room.contents(), [])


    def test_leave_beforeEntering(self):
        """
        You can't leave before you enter
        """
        room = Room()
        thing = MagicMock()
        thing.room = 'foo'
        self.assertRaises(NotInRoom, room.leave, thing)
        self.assertEqual(thing.room, 'foo', "Should not have changed the room")


    def test_broadcast(self):
        """
        You can broadcast messages to things in the room
        """
        room = Room()
        thing = MagicMock()

        room.enter(thing)
        room.broadcast('message')
        thing.messageReceived.assert_any_call('message')


    def test_enter_leave_broadcast(self):
        """
        Entering a room should cause a broadcast, as should leaving
        """
        room = Room()
        thing1 = MagicMock()
        room.enter(thing1)

        thing2 = MagicMock()
        thing2.identity.return_value = {'name': 'my name'}
        
        room.enter(thing2)
        thing1.messageReceived.assert_any_call({
            'event': 'enter',
            'who': {'name': 'my name'},
        })

        room.leave(thing2)
        thing1.messageReceived.assert_any_call({
            'event': 'leave',
            'who': {'name': 'my name'},
        })


