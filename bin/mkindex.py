#!/usr/bin/env python
from twisted.python.filepath import FilePath
import re
import json
from collections import defaultdict


r_title = re.compile('<title>(.*?)</title>', re.I | re.M | re.S)

def getInfo(fp):
    global r_title
    segments = fp.path.split('/')
    section = segments[-2]
    name = title = segments[-1]
    guts = fp.getContent()
    m = r_title.search(guts)
    if m:
        title = m.groups()[0]
    return section, name, title


def main(starting_path):
    r = defaultdict(lambda: {})
    for f in starting_path.walk():
        if f.isfile():
            section, name, title = getInfo(f)
            r[section][name] = {'title': title}
    return r


if __name__ == '__main__':
    me = FilePath(__file__)
    d = main(me.parent().parent().child('articles'))
    print json.dumps(d)