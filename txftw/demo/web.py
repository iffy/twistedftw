import json

from klein import Klein
from twisted.web.static import File
from twisted.internet import defer

from txftw.demo import message


def sseMsg(name, value):
    """
    Pack up some data as a Server Sent Event.
    """
    return 'event: %s\ndata: %s\n\n' % (name, json.dumps(value))



class DemoApp(object):

    app = Klein()


    def __init__(self, file_root, building, options):
        self.file_root = file_root
        self.building = building
        self.options = options


    @app.route('/')
    def index(self, request):
        request.redirect('static/index.html')


    @app.route('/static', branch=True)
    def static(self, request):
        return File(self.file_root.path)


    @app.route('/start')
    def start(self, request):
        key = self.building.createRoom()

        # add a guide
        from txftw.demo.guide import Guide
        guide = Guide(self.building, key, self.options)
        room = self.building.getRoom(key)
        room.enter(guide.name, guide)

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

        # add the user
        guy = WebRoomMember(request)
        room.enter('web', guy)
        request.write(sseMsg('who', list(room.contents())))
        request.write(sseMsg('name', guy.name))
        return defer.Deferred()


    @app.route('/room/<string:key>/say')
    def room_say(self, request, key):
        try:
            room = self.building.getRoom(key)
        except KeyError:
            request.setResponseCode(404)
            return None

        data = json.loads(request.content.read())
        msg = data.get('msg', '')
        who = data.get('who', '')

        request.setHeader('Content-Type', 'application/json')
        room.broadcast(message.msg(msg, who))



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
        self.request_alive = False
        if self.room:
            self.room.leave(self.name)


    def messageReceived(self, msg):
        if self.request_alive:
            self.request.write(sseMsg('d', msg))


