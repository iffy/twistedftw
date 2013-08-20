from twisted.trial.unittest import TestCase
from mock import MagicMock, create_autospec

from txftw.demo.room import Room, Building, NotInRoom



class RoomTest(TestCase):


    def test_enter(self):
        """
        Things can enter a room
        """
        room = Room()
        thing = MagicMock()

        room.enter('name', thing)
        thing.setRoom.assert_called_once_with(room)
        self.assertEqual(room.contents(), {'name': thing})


    def test_enter_twice(self):
        """
        Entering twice should raise an error.
        """
        room = Room()
        thing = MagicMock()
        
        room.enter('name', thing)
        self.assertRaises(Exception, room.enter, 'name', thing)


    def test_leave(self):
        """
        Things can leave a room
        """
        room = Room()
        thing = MagicMock()

        room.enter('thing', thing)
        thing.setRoom.reset_mock()

        room.leave('thing')
        thing.setRoom.assert_called_once_with(None)
        self.assertEqual(room.contents(), {})


    def test_leave_beforeEntering(self):
        """
        You can't leave before you enter
        """
        room = Room()
        thing = MagicMock()
        self.assertRaises(NotInRoom, room.leave, 'thing')
        self.assertEqual(thing.setRoom.call_count, 0,
                         "Should not have changed the room")


    def test_broadcast(self):
        """
        You can broadcast messages to things in the room
        """
        room = Room()
        thing = MagicMock()

        room.enter('name', thing)
        room.broadcast('message')
        thing.messageReceived.assert_any_call('message')


    def test_enter_leave_broadcast(self):
        """
        Entering a room should cause a broadcast, as should leaving
        """
        room = Room()
        thing1 = MagicMock()
        room.enter('t1', thing1)

        thing2 = MagicMock()
        
        room.enter('t2', thing2)
        thing1.messageReceived.assert_any_call({
            'event': 'enter',
            'who': 't2',
        })

        room.leave('t2')
        thing1.messageReceived.assert_any_call({
            'event': 'leave',
            'who': 't2',
        })


    def test_kick(self):
        """
        You can kick things out of a room
        """
        room = Room()
        thing1 = MagicMock()
        thing2 = MagicMock()

        room.enter('t1', thing1)
        thing1.setRoom.reset_mock()
        room.enter('t2', thing2)

        room.kick('t1')
        thing2.messageReceived.assert_any_call({
            'event': 'kick',
            'kicked': 't1',
        })
        thing1.setRoom.assert_called_once_with(None)
        self.assertEqual(room.contents(), {'t2': thing2})



class BuildingTest(TestCase):


    def test_create(self):
        """
        You can make new rooms
        """
        building = Building()
        key = building.createRoom()
        self.assertTrue(isinstance(key, str))

        room = building.getRoom(key)
        self.assertTrue(isinstance(room, Room))
        room2 = building.getRoom(key)
        self.assertEqual(room, room2, "Same key should return same room")


    def test_createRoom_uniqueKey(self):
        building = Building()
        k1 = building.createRoom()
        k2 = building.createRoom()
        self.assertNotEqual(k1, k2)


    def test_destroy(self):
        """
        You can destroy rooms (kicking everyone in them)
        """
        building = Building()
        key = building.createRoom()
        room = building.getRoom(key)
        room.kick = create_autospec(room.kick)

        thing1 = MagicMock()
        thing2 = MagicMock()
        room.enter('t1', thing1)
        room.enter('t2', thing2)

        building.destroyRoom(key)
        room.kick.assert_any_call('t1')
        room.kick.assert_any_call('t2')
        self.assertRaises(KeyError, building.getRoom, key)


