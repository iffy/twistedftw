from twisted.application import service, internet
from twisted.internet import endpoints, protocol
from twisted.web.server import Site
from twisted.python import log
from twisted.python import usage
from twisted.python.filepath import FilePath


from txftw.demo.room import Building
from txftw.demo.ssh import makeFactory
from txftw.demo.telnet import DemoFactory
from txftw.demo.web import DemoApp



class Options(usage.Options):

    optParameters = [
        # web
        ("web-endpoint", "w", 'tcp:8400',
            "string endpoint description for the webserver to listen on"),
        ("web-file-root", "f", "demo",
            "path to static files to be served"),

        # telnet
        ('telnet-endpoint', 't', 'tcp:8401',
            "String endpoint description for the telnet server to listen on"),

        # ssh
        ('ssh-endpoint', 's', 'tcp:8022',
            "String endpoint description for the ssh server to listen on"),
        ('ssh-keydir', None, '/tmp',
            "Directory with ssh keys named id_rsa and id_rsa.pub (will be "
            "created if they don't exist)"),
    ]



def makeService(options):
    from twisted.internet import reactor

    # common
    building = Building()

    # ssh
    endpoint = endpoints.serverFromString(reactor, options['ssh-endpoint'])
    factory = makeFactory()
    ssh_service = internet.StreamServerEndpointService(endpoint, factory)
    ssh_service.setName('SSH server')

    # telnet
    endpoint = endpoints.serverFromString(reactor, options['telnet-endpoint'])
    factory = DemoFactory(building)
    telnet_service = internet.StreamServerEndpointService(endpoint, factory)
    telnet_service.setName('Telnet server')

    # web
    endpoint = endpoints.serverFromString(reactor, options['web-endpoint'])
    web_app = DemoApp(FilePath(options['web-file-root']), building)
    site = Site(web_app.app.resource())
    web_service = internet.StreamServerEndpointService(endpoint, site)
    web_service.setName('Web server')

    # tie it all together
    ms = service.MultiService()
    web_service.setServiceParent(ms)
    telnet_service.setServiceParent(ms)
    ssh_service.setServiceParent(ms)

    return ms