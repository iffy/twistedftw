#!/usr/bin/env python
"""
I extract bits of python from HTML and generate a set of tests that can be run.
"""
from twisted.python.filepath import FilePath
import re
import sys
import json
from collections import defaultdict


r_code = re.compile(r'<!--\s*runcode\s+([^\s]+?)\s*-->\s*<pre.*?>(.*?)</pre>',
                    re.I | re.M | re.S)


def codeBlocks(fp):
    global r_code
    guts = fp.getContent()
    return r_code.findall(guts)


def testFilePath(starting_path, fp, case_name, test_root):
    without_ext = FilePath(fp.splitext()[0])
    segments = without_ext.segmentsFrom(starting_path)
    test_file = test_root
    for seg in segments:
        test_file = test_file.child(seg)
    test_file = test_file.child(case_name + '.py')
    return test_file


def main(starting_path, test_root):
    print starting_path
    r = defaultdict(lambda: [])
    for f in starting_path.walk():
        if f.isfile():
            for name, code in codeBlocks(f):
                tp = testFilePath(starting_path, f, name, test_root)
                if not tp.parent().exists():
                    tp.parent().makedirs()
                tp.setContent(code)
    return r


if __name__ == '__main__':
    root = FilePath(sys.argv[1])
    test_root = FilePath(sys.argv[2])
    main(root, test_root)