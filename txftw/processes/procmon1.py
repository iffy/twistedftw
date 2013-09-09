# Copyright (c) The TwistedFTW Team
# See LICENSE for details.

from twisted.internet import reactor
from twisted.application import service
from twisted.runner.procmon import ProcessMonitor
from twisted.python.filepath import FilePath
from twisted.python.procutils import which

application = service.Application("Web and Forwarder")

procmon_service = ProcessMonitor()
procmon_service.setServiceParent(application)

twistd = which('twistd')[0]

# serve /tmp on port 9905
procmon_service.addProcess('web',
    [twistd, '--nodaemon', '--pidfile=/tmp/web.pid',
     'web', '--port', 'tcp:9905', '--path', '/tmp'])

# add a port forwarder from 8805 to 9905 after 5 seconds
reactor.callLater(5, procmon_service.addProcess, 'pf',
    [twistd, '--nodaemon', '--pidfile=/tmp/pf.pid',
     'portforward', '--port', 'tcp:8805', '--dest_port', '9905'])
