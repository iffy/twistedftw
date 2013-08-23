from twisted.application import service, internet
from twisted.internet import endpoints, protocol
from twisted.web.server import Site
from twisted.python import log
from twisted.python import usage
from twisted.python.filepath import FilePath


from txftw.demo.room import Building
from txftw.demo.telnet import DemoFactory
from txftw.demo.web import DemoApp



class Options(usage.Options):

    optParameters = [
        ('domain', 'd', '127.0.0.1',
            "Domain name to use when giving out links"),

        ("web-endpoint", "w", 'tcp:8400',
            "string endpoint description for the webserver to listen on"),
        ("web-file-root", "f", "demo",
            "path to static files to be served"),

        ('telnet-endpoint', 't', 'tcp:8401',
            "String endpoint description for the telnet server to listen on"),
    ]



def makeService(options):
    from twisted.internet import reactor

    # common
    building = Building()

    # telnet
    endpoint = endpoints.serverFromString(reactor, options['telnet-endpoint'])
    factory = DemoFactory(building)
    telnet_service = internet.StreamServerEndpointService(endpoint, factory)
    telnet_service.setName('Telnet server')

    # web
    endpoint = endpoints.serverFromString(reactor, options['web-endpoint'])
    web_app = DemoApp(FilePath(options['web-file-root']), building, options)
    site = Site(web_app.app.resource())
    web_service = internet.StreamServerEndpointService(endpoint, site)
    web_service.setName('Web server')

    # tie it all together
    ms = service.MultiService()
    web_service.setServiceParent(ms)
    telnet_service.setServiceParent(ms)

    return ms