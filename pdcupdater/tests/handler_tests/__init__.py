from os.path import dirname
import unittest
import logging

import requests
import vcr

import fedmsg.utils

from nose.tools import raises

import pdcupdater.pdc


log = logging.getLogger(__name__)


cassette_dir = dirname(dirname(__file__)) + '/vcr-request-data/'

class BaseHandlerTest(unittest.TestCase):
    handler_path = None
    config = {}

    def setUp(self):
        if not self.handler_path:
            log.info("!! Warning - no handler path declared by base class.")

        config = self.config
        if self.handler_path:
            log.info("Initializing handler %s(%r)", self.handler_path, config)
            self.handler = fedmsg.utils.load_class(self.handler_path)(config)

        self.pdc = pdcupdater.pdc.PDCMock(config)

        log.info("Setting up vcr cassette in %s", cassette_dir)
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
