import json

from klein import Klein
from twisted.web.static import File
from twisted.internet import defer

from txftw.demo.room import AlreadyInTheRoom


def sseMsg(name, value):
    """
    Pack up some data as a Server Sent Event.
    """
    return 'event: %s\ndata: %s\n\n' % (name, json.dumps(value))



class DemoApp(object):

    app = Klein()


    def __init__(self, file_root, building):
        self.file_root = file_root
        self.building = building
        self._connected_clients = {}


    @app.route('/')
    def index(self, request):
        return '<a href="start">Start Demo</a>'


    @app.route('/start')
    def start(self, request):
        key = self.building.createRoom()
        request.redirect('room/' + key)


    @app.route('/room/<string:key>')
    def room(self, request, key):
        try:
            room = self.building.getRoom(key)
        except KeyError:
            request.setResponseCode(404)
            return None

        return File(self.file_root.child('room.html').path)


    @app.route('/room/<string:key>/events')
    def room_events(self, request, key):
        try:
            room = self.building.getRoom(key)
        except KeyError:
            request.setResponseCode(404)
            return None

        request.setHeader('Content-Type', 'text/event-stream')
        request.write(sseMsg('status', 'connected'))

        guy = WebRoomMember(request)
        name = 'web'
        while True:
            try:
                room.enter(name, guy)
                break
            except AlreadyInTheRoom:
                name = name + '_'
        request.write(sseMsg('who', list(room.contents())))
        return defer.Deferred()


    @app.route('/room/<string:key>/say')
    def room_say(self, request, key):
        try:
            room = self.building.getRoom(key)
        except KeyError:
            request.setResponseCode(404)
            return None



class WebRoomMember(object):
    """
    I am a thing that goes in a L{txftw.demo.room.Room} and communicates with
    the browser through server-sent events.
    """

    name = None
    room = None
    request_alive = True


    def __init__(self, request):
        self.request = request
        self.request.notifyFinish().addBoth(self._requestFinished)


    def setRoom(self, room, name):
        self.room = room
        self.name = name
        if room is None and self.request_alive:
            self.request.write(sseMsg('status', 'youleft'))


    def _requestFinished(self, response):
        print 'request finished', response
        self.request_alive = False
        if self.room:
            self.room.leave(self.name)


    def messageReceived(self, message):
        if self.request_alive:
            self.request.write(sseMsg('d', message))


