from os.path import dirname
import unittest

import requests
import vcr

from nose.tools import raises


cassette_dir = dirname(dirname(__file__)) + '/vcr-request-data/'

class BaseHandlerTest(unittest.TestCase):
    def setUp(self):
        print "setting up cassette in ", cassette_dir
        self.vcr = vcr.use_cassette(cassette_dir + self.id())
        self.vcr.__enter__()

    def tearDown(self):
        self.vcr.__exit__()

    def get_fedmsg(self, idx):
        # This gets recorded by vcr, so we'll have it on disk next time.
        url = 'https://apps.fedoraproject.org/datagrepper/id'
        response = requests.get(url, params=dict(id=idx))
        if not bool(response):
            raise IOError("Failed to talk to %r %r" % (response.url, response))
        return response.json()



class TestBaseHarness(BaseHandlerTest):
    @raises(IOError)
    def test_get_nonexistant_fedmsg(self):
        self.get_fedmsg('wat')

    def test_get_fedmsg(self):
        idx = '2015-6c98c8e3-0dcb-497d-a0d8-0b3d026a4cfb'
        msg = self.get_fedmsg(idx)
        self.assertEquals(msg['msg']['user']['username'], 'ralph')
