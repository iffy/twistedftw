class NotInRoom(Exception): pass


from uuid import uuid4
from hashlib import sha1

from txftw.demo import message



class Room(object):
    """
    I am a room where named things can gather and pass around messages.
    """


    def __init__(self):
        self._contents = {}


    def enter(self, name, thing):
        """
        C{thing} is entering this room under the alias C{name}.

        @param name: Name of the thing entering this room.  This must be unique
            within this room.
        @param thing: Some object with C{setRoom(room, name)} and
            C{messageReceived(message)} methods.
        """
        i = 1
        orig = name
        while name in self._contents:
            name = orig + str(i)
            i += 1
        thing.setRoom(self, name)
        self._contents[name] = thing
        self.broadcast(message.enter(name))


    def leave(self, name):
        """
        The thing named C{name} is leaving this room.
        """
        try:
            thing = self._contents.pop(name)
        except KeyError:
            raise NotInRoom(name)
        thing.setRoom(None, name)
        self.broadcast(message.leave(name))


    def kick(self, name):
        """
        The thing named C{name} is being kicked out of the room.
        """
        self.broadcast(message.kick(name))
        self.leave(name)


    def contents(self):
        """
        List all the things in the room.
        """
        return self._contents


    def broadcast(self, message):
        """
        Send a message to all things in this room.
        """
        for name,thing in self._contents.items():
            thing.messageReceived(message)



class Building(object):
    """
    I am a building full of rooms.
    """


    def __init__(self):
        self._rooms = {}


    def _newKeyAttempt(self):
        return sha1(str(uuid4())).hexdigest()[:8]

    def createRoom(self):
        """
        Provision a new room.

        @return: A C{key} to be used when calling L{getRoom} and L{destroyRoom}.
        """
        key = self._newKeyAttempt()
        while key in self._rooms:
            key = self._newKeyAttempt()
        self._rooms[key] = Room()
        return key


    def getRoom(self, key):
        """
        Get the L{Room} associated with a C{key}.
        """
        return self._rooms[key]


    def destroyRoom(self, key):
        """
        Destroy a room (kicking everyone out of it)
        """
        room = self.getRoom(key)
        del self._rooms[key]
        for thing in list(room.contents()):
            room.kick(thing)



