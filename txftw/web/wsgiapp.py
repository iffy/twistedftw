# wsgiapp.py
# Copyright (c) The TwistedFTW Team
# See LICENSE for details.
def application(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    return ['Hello, world!']