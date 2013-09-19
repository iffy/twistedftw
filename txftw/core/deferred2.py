# Copyright (c) The TwistedFTW Team
# See LICENSE for details.
import select
import socket

class ExampleReactor(object):
    
    timeout = 10
    running = True
    
    def __init__(self):
        self.sockets = []
        self.connections = []
        self.handler = lambda s,d:None

    def addSocket(self, socket):
        self.sockets.append(socket)

    def rmSocket(self, socket):
        self.sockets.remove(socket)

    def setFunctionToBeCalledWhenThereIsData(self, func):
        self.handler = func

    def _doIteration(self):
        sockets = self.sockets + self.connections
        r, w, e = select.select(sockets, [], [], self.timeout)

        for readable in r:
            if readable in self.sockets:
                conn_socket, addr = readable.accept()
                self.connections.append(conn_socket)
            elif readable in self.connections:
                data = readable.recv(8192)
                if not data:
                    self.connections.remove(readable)
                else:
                    self.handler(readable, data)

    def run(self):
        while self.running:
            self._doIteration()


class CallbackRegistry(object):

    def __init__(self):
        self.callbacks = []

    def addCallback(self, function):
        self.callbacks.append(function)

    def callback(self, value):
        for callback in self.callbacks:
            value = callback(value)


def getSomeDataThenDisconnect(reactor, port):
    # Start a server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', port))
    s.setblocking(0)
    s.listen(1)

    # The registry for the caller of this function to use.
    registry = CallbackRegistry()

    def dataReceived(addr, data):
        # Inform the registry that there is data
        registry.callback(data)
        
        # Stop listening for more data and stop the reactor
        reactor.rmSocket(s)
        reactor.running = False

    reactor.setFunctionToBeCalledWhenThereIsData(dataReceived)

    # Tell the reactor to wait for events from this socket.
    reactor.addSocket(s)

    # Return the CallbackRegistry instance so that the user can attach their
    # own callbacks.
    return registry


def main():
    reactor = ExampleReactor()
    
    # ask for some data and get a CallbackRegistry in return.
    registry = getSomeDataThenDisconnect(reactor, 7777)

    # register some callbacks to do things with the data once it arrives.
    def capitalize(x):
        return x.upper()
    
    def printResult(x):
        print x

    registry.addCallback(capitalize)
    registry.addCallback(printResult)

    # start the reactor
    reactor.run()


if __name__ == '__main__':
    main()
