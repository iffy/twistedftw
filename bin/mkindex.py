#!/usr/bin/env python
# Copyright (c) The TwistedFTW Team
# See LICENSE for details.

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
    name = title = segments[-1].split('.')[0]
    guts = fp.getContent()
    m = r_title.search(guts)
    if m:
        title = m.groups()[0]
    return section, name, title


def main(starting_path):
    r = defaultdict(lambda: {'name': '', 'title': '', 'articles':[]})
    for f in starting_path.walk():
        try:
            segments = f.segmentsFrom(starting_path)
            section = segments[0]
        except:
            continue
        if f.isfile() and f.basename() == 'contents':
            for filename in f.getContent().split('\n'):
                try:
                    section, name, title = getInfo(f.sibling(filename))
                    r[section]['articles'].append({'name': name, 'title': title})
                except Exception as e:
                    sys.stderr.write(str(e) + '\n')
        elif f.isfile() and f.basename() == 'title':
            r[section]['title'] = f.getContent().strip()
            r[section]['name'] = f.parent().basename()
    return r


if __name__ == '__main__':
    me = FilePath(__file__)
    d = main(me.parent().parent().child('articles'))
    print json.dumps(d)