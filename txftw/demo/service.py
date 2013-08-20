from twisted.application import service, internet
from twisted.internet import endpoints, protocol
from twisted.web.server import Site
from twisted.python import log
from twisted.python import usage
from twisted.python.filepath import FilePath


from txftw.demo.room import Building
from txftw.demo.web import DemoApp



class Options(usage.Options):

    optParameters = [
        ("web-endpoint", "w", 'tcp:8400',
            "string endpoint description for the webserver to listen on"),
        ("web-file-root", "f", "demo",
            "path to static files to be served"),
    ]



def makeService(options):
    from twisted.internet import reactor

    # common
    building = Building()

    # web
    endpoint = endpoints.serverFromString(reactor, options['web-endpoint'])
    web_app = DemoApp(FilePath(options['web-file-root']), building)
    site = Site(web_app.app.resource())
    web_service = internet.StreamServerEndpointService(endpoint, site)
    web_service.setName('Web Server')

    # tie it all together
    ms = service.MultiService()
    web_service.setServiceParent(ms)

    return ms