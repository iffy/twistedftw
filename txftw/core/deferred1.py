# Copyright (c) The TwistedFTW Team
# See LICENSE for details.
class CallbackRegistry(object):

    def __init__(self):
        self.callbacks = []

    def addCallback(self, function):
        self.callbacks.append(function)

    def callback(self, value):
        # We have data to give to the callbacks.  Give it to them!
        for callback in self.callbacks:
            value = callback(value)
