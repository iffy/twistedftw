from twisted.internet import reactor
from txftw.demo import message



class Guide(object):

    name = 'Guido'
    room = None
    state = 'init'


    def __init__(self, building, room_key):
        self._building = building
        self._key = room_key


    def setRoom(self, room, name):
        self.room = room
        self.name = name
        self._finished_outcomes = []
        self.achievements = []
        self.outcomes = [
            SayAnything(self),
            SecondWebConnection(self),
            TelnetConnection(self, '127.0.0.1', 8401),

            # this needs to be last
            EveryoneLeaves(self),
        ]
        self.outcomes[0].start()


    def say(self, msg):
        if self.room:
            self.room.broadcast(message.msg(msg, self.name))


    def messageReceived(self, msg):
        if msg['event'] == 'msg' and msg['who'] == self.name:
            # ignore messages from myself
            return

        for outcome in (x for x in self.outcomes if x.receiving):
            outcome.messageReceived(msg)


    def outcomeAchieved(self, outcome):
        self._finished_outcomes.append(outcome)
        self.outcomes.remove(outcome)
        self.achievements.append(outcome.__class__.__name__)
        if self.outcomes:
            self.outcomes[0].start()


    def destroyRoom(self):
        print 'destroying room', self._key
        self._building.destroyRoom(self._key)



class Outcome(object):
    """
    @ivar receiving: Must be C{True} for messages to be sent.
    """

    achieved = False
    started = False
    receiving = False

    def __init__(self, guide):
        self.guide = guide
        self._pending_thoughts = []


    def messageReceived(self, msg):
        pass


    def start(self):
        self.receiving = True
        self.started = True


    def say(self, msg):
        self.guide.say(msg)


    def sayLater(self, interval, msg):
        d = reactor.callLater(interval, self.guide.say, msg)
        self._pending_thoughts.append(d)


    def cancelPendingThoughts(self):
        while self._pending_thoughts:
            t = self._pending_thoughts.pop(0)
            if not t.called:
                t.cancel()


    def achieve(self):
        self.cancelPendingThoughts()
        self.achieved = True
        self.guide.outcomeAchieved(self)



class EveryoneLeaves(Outcome):

    receiving = True

    def messageReceived(self, msg):
        if msg['event'] == 'leave':
            if len(self.guide.room.contents()) == 1:
                # Guido's the only one in the room
                self.guide.destroyRoom()



class SayAnything(Outcome):

    receiving = True

    def messageReceived(self, msg):
        if msg['event'] == 'msg':
            self.achieve()
            self.sayLater(1, "Oh good, you're there!")


    def start(self):
        Outcome.start(self)
        self.sayLater(1, "Hello!  I'm %s, a bot.  How are you?" % (self.guide.name,))
        self.sayLater(8, "Hello?")
        self.sayLater(17, "Type something so I know you're there.")



class SecondWebConnection(Outcome):

    receiving = True
    entrants = 0

    def messageReceived(self, msg):
        if msg['event'] == 'enter' and msg['who'].count('web'):
            self.entrants += 1
        if self.entrants >= 2:
            self.achieve()
            self.sayLater(1, "Hello to both of you!")

    def start(self):
        Outcome.start(self)
        self.sayLater(3, "We are chatting in real time.")
        self.sayLater(4, "Open this page in another tab to see")



class TelnetConnection(Outcome):

    def __init__(self, guide, ip, port):
        Outcome.__init__(self, guide)
        self.ip = ip
        self.port = port


    def messageReceived(self, msg):
        if msg['event'] == 'enter' and msg['who'].count('telnet'):
            self.achieve()
            self.sayLater(1, "Voila!  Telnet talking to HTTP!")


    def start(self):
        Outcome.start(self)
        self.sayLater(5, "You're connected through a browser using the HTTP "
                         "protocol.You can also connect using telnet.  In a "
                         "terminal, type telnet %s %s" % (self.ip, self.port))
        self.sayLater(7, "It will ask for this key: %s" % (self.guide._key,))


