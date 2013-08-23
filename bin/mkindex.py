#!/usr/bin/env python
from twisted.python.filepath import FilePath
import re
import sys
import json
from collections import defaultdict


r_title = re.compile('<h1>(.*?)</h1>', re.I | re.M | re.S)

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
    r = defaultdict(lambda: [])
    for f in starting_path.walk():
        if f.isfile() and f.basename() == 'contents':
            for filename in f.getContent().split('\n'):
                try:
                    section, name, title = getInfo(f.sibling(filename))
                    r[section].append({'name': name, 'title': title})
                except Exception as e:
                    sys.stderr.write(str(e) + '\n')
    return r


if __name__ == '__main__':
    me = FilePath(__file__)
    d = main(me.parent().parent().child('articles'))
    print json.dumps(d)