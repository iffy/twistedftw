# test_mktemp.py
# Copyright (c) The TwistedFTW Team
# See LICENSE for details.
from twisted.trial.unittest import TestCase
from twisted.python.filepath import FilePath


class InventoryReaderTest(TestCase):

    def test_onePerLine(self):
        """
        L{inventoryReader} should return strings, one per line from
        the file.
        """
        fp = FilePath(self.mktemp())
        fp.setContent('something\ncool')
        self.assertEqual(list(inventoryReader(fp.path)), ['something', 'cool'])

    def test_comments(self):
        """
        Lines that begin with # should be excluded
        """
        fp = FilePath(self.mktemp())
        fp.setContent('something\n#commented\ncool')
        self.assertEqual(list(inventoryReader(fp.path)), ['something', 'cool'])

    def test_ignoreBlanks(self):
        """
        Blank lines should not be returned
        """
        fp = FilePath(self.mktemp())
        fp.setContent('something\n\n\n\n')
        self.assertEqual(list(inventoryReader(fp.path)), ['something'])


def inventoryReader(filename):
    for line in open(filename, 'r'):
        line = line.strip()
        if line and not line.startswith('#'):
            yield line