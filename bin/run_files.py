#!/usr/bin/env python
# Copyright (c) TwistedFTW
# See LICENSE for details.

import sys

from twisted.python.filepath import FilePath
from twisted.internet.task import react
from twisted.internet import defer, utils
from twisted.python import log


def finished((out,err,code), name):
    if code != 0:
        log.msg('Failed', system=name)
    log.msg(out, system=name+' out')
    log.msg(err, system=name+' err')
    log.msg(code, system=name+' rc')
    return code

def runFile(fp, name):
    log.msg('Started', system=name)
    d = utils.getProcessOutputAndValue(sys.executable, [fp.path], env=None)
    return d.addBoth(finished, name)


def makeName(fp, root):
    return '/'.join(fp.segmentsFrom(root))


def didItFail(res):
    res = set(res)
    if res != set([0]):
        raise Exception("It failed")
    log.msg('Success!')

def main(reactor, root):
    dlist = []
    for f in root.walk():
        if f.path.endswith('.py'):
            dlist.append(runFile(f, makeName(f, root)))
    
    d = defer.gatherResults(dlist)
    return d.addBoth(didItFail)


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    root = FilePath(sys.argv[1])
    react(main, [root])