from twisted.internet.protocol import Protocol
from twisted.cred.portal import Portal
from twisted.cred.checkers import FilePasswordDB, InMemoryUsernamePasswordDatabaseDontUse
from twisted.conch.ssh.factory import SSHFactory
from twisted.internet import reactor
from twisted.conch.ssh.keys import Key
from twisted.conch.interfaces import IConchUser
from twisted.conch.avatar import ConchUser
from twisted.conch.recvline import HistoricRecvLine
from twisted.conch.telnet import TelnetTransport, TelnetBootstrapProtocol
from twisted.conch.manhole_ssh import TerminalRealm, ConchFactory
from twisted.conch.insults import insults
from twisted.conch.ssh.session import (
    SSHSession, SSHSessionProcessProtocol, wrapProtocol)
from twisted.conch.scripts import ckeygen

from twisted.python.filepath import FilePath

# with open('id_rsa') as privateBlobFile:
#     privateBlob = privateBlobFile.read()
#     privateKey = Key.fromString(data=privateBlob)

# with open('id_rsa.pub') as publicBlobFile:
#     publicBlob = publicBlobFile.read()
#     publicKey = Key.fromString(data=publicBlob)

from txftw.demo.telnet import DemoProtocol


class KeyPair(object):

    _private_key = None
    _public_key = None


    def __init__(self, root, filename='id_rsa', passphrase='foo'):
        """
        @param root: root to a directory where keys ought to be.
        @param passphrase: Passphrase keys are encrypted with.  A default of
            C{'foo'} is used because of U{http://tm.tl/5998}.
        """
        self.root = FilePath(root)
        self.filename = filename
        self.passphrase = passphrase


    def getPrivateKey(self, generate=True):
        if self._private_key:
            return self._private_key
        path = self.root.child(self.filename)
        if path.exists():
            with open(path.path) as fh:
                blob = fh.read()
                self._private_key = Key.fromString(data=blob,
                                                   passphrase=self.passphrase)
        elif generate:
            # generate it through hacky means
            options = ckeygen.GeneralOptions()
            options['type'] = 'rsa'
            options['bits'] = 1024
            options['pass'] = self.passphrase
            options['filename'] = path.path
            ckeygen.generateRSAkey(options)
            return self.getPrivateKey(generate=False)

        return self._private_key


    def getPublicKey(self):
        if self._public_key:
            return self._public_key

        # get it from the private key
        key = self.getPrivateKey()
        self._public_key = key.public()
        return self._public_key



class SSHBridgeProtocol(HistoricRecvLine):

    #def __init__(self, proto):
    #    self.proto = proto


    def connectionMade(self):
        HistoricRecvLine.connectionMade(self)
        #self.keyHandlers[]


    def lineReceived(self, line):
        print 'line received', line



class SimpleSession(SSHSession):
    name = 'session'

    def request_pty_req(self, data):
        print 'pty_req'
        return True

    def request_shell(self, data):
        protocol = SSHBridgeProtocol(DemoProtocol())
        transport = SSHSessionProcessProtocol(self)
        protocol.makeConnection(transport)
        transport.makeConnection(wrapProtocol(protocol))
        self.client = transport
        return True



class SimpleRealm(object):

    def requestAvatar(self, avatarId, mind, *interfaces):
        print 'avatarId', avatarId
        user = ConchUser()
        user.channelLookup['session'] = SimpleSession
        return IConchUser, user, lambda:None



class Factory(SSHFactory):


    def __init__(self, keypair):
        self.privateKeys = {'ssh-rsa': keypair.getPrivateKey()}
        self.publicKeys = {'ssh-rsa': keypair.getPublicKey()}
        self.portal = Portal(SimpleRealm())
        self.portal.registerChecker(InMemoryUsernamePasswordDatabaseDontUse(matt='foo'))


def makeFactory():
    def chainProtocolFactory():
        return insults.ServerProtocol(SSHBridgeProtocol)
    realm = TerminalRealm()
    realm.chainedProtocolFactory = chainProtocolFactory
    portal = Portal(realm)
    portal.registerChecker(InMemoryUsernamePasswordDatabaseDontUse(matt='foo'))
    return ConchFactory(portal)

# factory = SSHFactory()
# factory.privateKeys = {'ssh-rsa': privateKey}
# factory.publicKeys = {'ssh-rsa': publicKey}
# factory.portal = Portal(SimpleRealm())
# factory.portal.registerChecker(AllowAnonymousAccess())




# reactor.listenTCP(2022, factory)
# reactor.run()