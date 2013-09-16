# Copyright (c) The TwistedFTW Team
# See LICENSE for details.

from twisted.internet import reactor
from twisted.web.wsgi import WSGIResource
from klein import Klein
from flask import Flask


def makeFlaskApp(name):
    """
    Create a new Flask app that identifies itself as C{name}.
    """
    flask_app = Flask(__name__)
    @flask_app.route('/')
    def index():
        return 'I am ' + name + '\n'
    return flask_app


class FlaskMaker(object):
    """
    I create Flask subapps on demand, but only allow 3 requests to be made to
    the subapps.
    """

    app = Klein()
    lives = 3

    def __init__(self):
        self.running_flask_apps = {}


    @app.route('/')
    def status(self, request):
        """
        Get the status of all the known Flask subapps including their name and
        how many lives they have left.
        """
        lines = []
        for prefix in sorted(self.running_flask_apps):
            data = self.running_flask_apps[prefix]
            lines.append('%s, lives: %s' % (prefix, data.get('lives')))
        request.setHeader('Content-Type', 'text/plain')
        if not lines:
            return 'No running apps\n'
        return '\n'.join(lines) + '\n'


    @app.route('/<prefix>', branch=True)
    def subapp(self, request, prefix):
        """
        Access a Flask subapp, unless the subapp's lives have been consumed.
        """
        flask_data = self._maybeCreateFlaskApp(prefix)

        # use up a life
        resource = flask_data.get('resource')
        flask_data['lives'] -= 1

        if flask_data['lives'] == 0:
            flask_data.pop('resource')

        if flask_data['lives'] <= 0:
            request.setResponseCode(410)
            return 'Nevermore\n'
        
        return resource


    def _maybeCreateFlaskApp(self, prefix):
        """
        Create a Flask app that will return the given prefix in the response
        unless there was one already created.
        """
        data = self.running_flask_apps.get(prefix)
        if data is None:
            flask_app = makeFlaskApp(prefix)
            wsgi_resource = WSGIResource(reactor, reactor.getThreadPool(),
                                         flask_app.wsgi_app)
            data = self.running_flask_apps[prefix] = {
                'resource': wsgi_resource,
                'lives': self.lives,
            }
        return data


if __name__ == '__main__':
    distributor = FlaskMaker()
    distributor.app.run('localhost', 8080)