# Copyright (c) The TwistedFTW Team
# See LICENSE for details.
from twisted.internet import protocol, task, defer
import re
import random


class RandomGamePlayer(protocol.ProcessProtocol):
    """
    I play the game, but not very well.
    """
    
    r_min_max = re.compile(r'Guess the number ([0-9]+) to ([0-9]+)')

    def __init__(self):
        self.done = defer.Deferred()
        self.last_guess = None
        self.buf = ''
        self.min_val = None
        self.max_val = None

    def outReceived(self, data):
        self.buf += data
        while self.buf.count('\n'):
            line, rest = self.buf.split('\n', 1)
            self.buf = rest
            self.lineReceived(line)

    def lineReceived(self, line):
        print line
        if line.startswith('Guess'):
            self.makeGuess(line)
        elif line.count('too high'):
            self.guessWasHigh()
        elif line.count('too low'):
            self.guessWasLow()


    def makeGuess(self, line):
        if not self.min_val:
            match = self.r_min_max.match(line)
            self.min_val = int(match.groups()[0])
            self.max_val = int(match.groups()[1])

        self.last_guess = random.randint(self.min_val, self.max_val)
        self.transport.write(str(self.last_guess) + '\n')
    
    def guessWasHigh(self):
        """
        Called when my C{last_guess} was too high.
        """

    def guessWasLow(self):
        """
        Called when my C{last_guess} was too low.
        """

    def processEnded(self, status):
        self.done.callback(self)


def main(reactor, script):
    proto = RandomGamePlayer()
    reactor.spawnProcess(proto, script, [script], usePTY=True)
    return proto.done


task.react(main, ['guessinggame.py'])