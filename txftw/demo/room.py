class AlreadyInTheRoom(Exception): pass
class NotInRoom(Exception): pass


class Room(object):
    """
    I am a room where things can gather and pass around messages.
    """


    def __init__(self):
        self._contents = []


    def enter(self, thing):
        """
        C{thing} is entering this room.
        """
        if thing in self._contents:
            raise AlreadyInTheRoom(thing)
        thing.room = self
        self._contents.append(thing)
        self.broadcast({
            'event': 'enter',
            'who': thing.identity()
        })


    def leave(self, thing):
        """
        C{thing} is leaving this room.
        """
        try:
            self._contents.remove(thing)
        except ValueError:
            raise NotInRoom(thing)
        thing.room = None
        self.broadcast({
            'event': 'leave',
            'who': thing.identity(),
        })


    def contents(self):
        """
        List all the things in the room.
        """
        return self._contents


    def broadcast(self, message):
        """
        Send a message to all things in this room.
        """
        for thing in self._contents:
            thing.messageReceived(message)