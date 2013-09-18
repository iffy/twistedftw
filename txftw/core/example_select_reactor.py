# Copyright (c) The TwistedFTW Team
# See LICENSE for details.
import select
import socket

class ExampleReactor(object):

    # arbitrary timeout in seconds
    timeout = 10

    def __init__(self):
        self.sockets = []
        self.connections = []
        self.handler = lambda s,d:None

    def addSocket(self, socket):
        # Watch a socket for connections.
        self.sockets.append(socket)

    def setFunctionToBeCalledWhenThereIsData(self, func):
        # Set a function to be called every time data arrives on a socket.  The
        # function must take two arguments: a socket instance and the data that
        # was read.
        self.handler = func

    def _doIteration(self):
        # The "magical" select function will return when either
        #   a) a socket in self.sockets has a connection to be made or
        #   b) when something in self.connections has data to be read or
        #   c) when self.timeout seconds have elapsed.
        sockets = self.sockets + self.connections
        print 'waiting'
        r, w, e = select.select(sockets, [], [], self.timeout)

        # r is a list of sockets and connections that have data ready.
        # Each readable will either be a socket awaiting connections or else a
        # connection with data to be read.
        for readable in r:

            # Handle listening sockets
            if readable in self.sockets:
                # This readable is a listening socket that can now be
                # connected.  Let's accept the connection and add it to the
                # list of connections.
                conn_socket, addr = readable.accept()
                self.connections.append(conn_socket)

            # Handle connections
            elif readable in self.connections:
                # This readable is a connected socket with data available to be
                # read.  Let's read some (or all) of the data and call the
                # handler function with it.
                data = readable.recv(8192)
                if not data:
                    # No data is available for reading.  This is a signal
                    # that they have disconnected.  Stop watching this
                    # connection for data.
                    self.connections.remove(readable)
                else:
                    self.handler(readable, data)

    def run(self):
        # Run forever (or until the process is killed)
        while True:
            self._doIteration()



def exampleApp():
    # start a "server" on port 7001
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 7001))
    s.setblocking(0)
    s.listen(1)

    # create a reactor and register the server socket with it.
    reactor = ExampleReactor()
    reactor.addSocket(s)

    # make a function that will print out data received and tell the reactor
    # to call the function every time data is received.
    def dataReceived(s, data):
        print 'from %s received %r' % (s.getpeername(), data)
    reactor.setFunctionToBeCalledWhenThereIsData(dataReceived)

    # start the reactor
    reactor.run()


if __name__ == '__main__':
    exampleApp()
