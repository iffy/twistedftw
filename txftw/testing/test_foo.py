# Copyright (c) The TwistedFTW Team
# See LICENSE for details.

# test_foo.py
import unittest

class TestThings(unittest.TestCase):

    def test_concatenation(self):
        self.assertEqual('a' + 'b', 'ab')

    def test_addition(self):
        self.assertEqual(1 + 2, 3)