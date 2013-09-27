# Copyright (c) The TwistedFTW Team
# See LICENSE for details.
# annoybot.py
from twisted.words.protocols import irc
from twisted.internet import reactor, endpoints
from twisted.python import log
from datetime import datetime, timedelta
import re
import sys


class Annoyer(irc.IRCClient):
    
    nickname = 'annoy'
    channel = '#foo'
    default_fuse_msg = 'BOOM!'

    r_timestr = re.compile(r'''
        ([0-2]?[0-9])       # hours
        (?:\:([0-5][0-9]))? # minutes
        (am|pm)?            # am/pm
        ''', re.I | re.X)


    def __init__(self, clock=None):
        self.clock = clock or reactor


    def signedOn(self):
        self.join(self.channel)


    def now(self):
        return datetime.now()


    def timeStrToDatetime(self, input_str):
        """
        Convert a string representation of a time to the soonest possible
        datetime after the current time.

        For instance, if it's 3:22pm right now, then

            '4'       -> 4pm
            '3'       -> 3am the next day
            '2:30pm'  -> 2:30pm the next day
            '4am'     -> 4am the next day

        """
        m = self.r_timestr.match(input_str)
        hours, minutes, ampm = m.groups()
        
        hours = int(hours)
        hour_interval = 12
        if ampm == 'pm':
            hours += 12
            hour_interval = 24
        elif ampm == 'am':
            hours %= 12
            hour_interval = 24
        
        minutes = int(minutes or '0')
        
        now = self.now()
        t = now.replace(hour=hours, minute=minutes, second=0)
        while t <= now:
            t += timedelta(hours=hour_interval)
        return t


    def lightFuse(self, channel, seconds, msg=None, user=None):
        """
        Light a fuse for a message to be sent on a channel
        in C{seconds} seconds.
        """
        msg = msg or self.default_fuse_msg
        if user:
            msg = '%s: %s' % (user, msg)
        self.clock.callLater(seconds, self.msg, channel, msg)


    def privmsg(self, user, channel, msg):
        """
        Handle a message being received
        """
        user = user.split('!', 1)[0]
        response_prefix = user
        
        # private message
        if channel == self.nickname:
            # prepare to send a private message
            channel = user
            response_prefix = None

        # interpret the message as a command
        msg = msg.strip()
        parts = msg.split(' ')

        if msg.startswith('@'):
            # @ command
            t = self.timeStrToDatetime(parts[0][1:])
            diff = t - self.now()
            self.lightFuse(channel, diff.seconds, ' '.join(parts[1:]),
                           response_prefix)
        
        elif msg.lower().startswith('t-'):
            # t- command
            seconds = int(parts[0][2:])
            self.lightFuse(channel, seconds, ' '.join(parts[1:]),
                           response_prefix)


    def alterCollidedNick(self, nickname):
        return nickname + '_'


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    server, botname, room = sys.argv[1:]
    
    proto = Annoyer()
    proto.channel = '#'+room
    proto.nickname = botname

    ep = endpoints.clientFromString(reactor, server)
    endpoints.connectProtocol(ep, proto)
    reactor.run()
