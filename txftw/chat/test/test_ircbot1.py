# Copyright (c) The TwistedFTW Team
# See LICENSE for details.
from twisted.trial.unittest import TestCase
from twisted.internet.task import Clock
from twisted.internet import reactor
from datetime import datetime

from mock import create_autospec


from txftw.chat.ircbot1 import Annoyer


class AnnoyerTest(TestCase):


    def test_defaultClock(self):
        a = Annoyer()
        self.assertEqual(a.clock, reactor)


    def test_lightFuse(self):
        """
        You can set a fuse and have it go off, causing a message to be sent.
        """
        a = Annoyer(clock=Clock())
        a.default_fuse_msg = 'foo'
        a.msg = create_autospec(a.msg)
        a.lightFuse('channel', 10)
        a.clock.advance(10)
        a.msg.assert_called_once_with('channel', 'foo')


    def test_lightFuse_customMessage(self):
        """
        You can set a fuse and have it go off with a customer message.
        """
        a = Annoyer(clock=Clock())
        a.msg = create_autospec(a.msg)
        a.lightFuse('channel', 10, 'heyo')
        a.clock.advance(10)
        a.msg.assert_called_once_with('channel', 'heyo')


    def test_lightFuse_toUser(self):
        """
        You can set a fuse and have it go to a certain channel, directed at
        a certain user.
        """
        a = Annoyer(clock=Clock())
        a.msg = create_autospec(a.msg)
        a.lightFuse('channel', 10, user='bob')
        a.clock.advance(10)
        a.msg.assert_called_once_with('channel', 'bob: BOOM!')


    def test_now(self):
        """
        Should return now
        """
        a = Annoyer()
        t1 = a.now()
        t2 = datetime.now()
        diff = t2 - t1
        self.assertTrue(diff.seconds < 2)


    def test_timeStrToDatetime(self):
        """
        You can convert time strings to datetime objects.
        """
        a = Annoyer(clock=Clock())
        now = datetime(2000, 1, 12, 3, 22, 5)
        a.now = create_autospec(a.now, return_value=now)

        self.assertEqual(a.timeStrToDatetime('4'),
                         datetime(2000, 1, 12, 4, 0, 0),
                         "Should find the next hour after this one")

        self.assertEqual(a.timeStrToDatetime('3'),
                         datetime(2000, 1, 12, 15, 0, 0),
                         "Should do PM hours")

        self.assertEqual(a.timeStrToDatetime('4pm'),
                         datetime(2000, 1, 12, 16, 0, 0),
                         "Should do explicit PM hours")

        self.assertEqual(a.timeStrToDatetime('3:30'),
                         datetime(2000, 1, 12, 3, 30, 0),
                         "Should do minutes")

        self.assertEqual(a.timeStrToDatetime('3am'),
                         datetime(2000, 1, 13, 3, 0, 0),
                         "Should do AM next day")

        self.assertEqual(a.timeStrToDatetime('3:28pm'),
                         datetime(2000, 1, 12, 15, 28, 0),
                         "Should do PM hours and minutes")

