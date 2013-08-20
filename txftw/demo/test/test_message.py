from twisted.trial.unittest import TestCase


from txftw.demo.message import enter, leave, msg



class msgTest(TestCase):


    def test_unicode(self):
        r = msg(u'\N{SNOWMAN}', u'\N{SNOWMAN}')
        self.assertEqual(r['msg'], u'\N{SNOWMAN}'.encode('utf-8'))
        self.assertEqual(r['who'], u'\N{SNOWMAN}'.encode('utf-8'))
