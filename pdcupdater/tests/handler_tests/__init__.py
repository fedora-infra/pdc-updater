from os.path import dirname
import functools
import unittest
import logging

import requests
import vcr

import fedmsg.utils

from nose.tools import raises

import pdc_client.test_helpers

log = logging.getLogger(__name__)


cassette_dir = dirname(dirname(__file__)) + '/vcr-request-data/'


def mock_pdc(function):
    @functools.wraps(function)
    @pdc_client.test_helpers.mock_api
    def wrapper(self, pdc, *args, **kwargs):
        # Mock out POST endpoints
        pdc.add_endpoint('global-components', 'POST', 'wat')
        pdc.add_endpoint('release-components', 'POST', 'wat')
        pdc.add_endpoint('compose-images', 'POST', 'wat')
        pdc.add_endpoint('compose-rpms', 'POST', 'wat')
        pdc.add_endpoint('persons', 'POST', 'wat')
        pdc.add_endpoint('rpms', 'POST', 'wat')

        # Mock out GET endpoints
        pdc.add_endpoint('persons', 'GET', {
            'count': 2,
            'next': None,
            'previous': None,
            'results': [
                {'username': 'ralph', 'email': 'ralph@fedoraproject.org'},
                {'username': 'lmacken', 'email': 'lmacken@fedoraproject.org'},
            ],
        })

        pdc.add_endpoint('rpms', 'GET', {
            'count': 2,
            'next': None,
            'previous': None,
            'results': [{
                'name': 'dvisvgm',
                'arch': 'src',
                'epoch': None,
                'version': '1.11',
                'release': '1.el7',
                'linked_releases': ['epel7'],
                'srpm_name': 'undefined...',
            }, {
                'name': 'rubygem-jmespath-doc',
                'arch': 'noarch',
                'epoch': None,
                'version': '1.1.3',
                'release': '1.el7',
                'linked_releases': ['epel7'],
                'srpm_name': 'undefined...',
            }],
        })

        pdc.add_endpoint('composes', 'GET', {
            'count': 2,
            'next': None,
            'previous': None,
            'results': [{
                "acceptance_testing": "ComposeAcceptanceTestingState.name",
                "compose_date": "20151130",
                "compose_id": "Fedora-24-20151130.n.2",
                "compose_label": "Fedora-24-20151130.n.2",
                "compose_respin": "2",
                "compose_type": "nightly",
                "deleted": "boolean",
                "linked_releases": [],
                "release": "rawhide",
                "rpm_mapping_template": "some url",
                "rtt_tested_architectures": { },
                "sigkeys": [],
            }],
        })

        return function(self, pdc, *args, **kwargs)
    return wrapper


class BaseHandlerTest(unittest.TestCase):
    maxDiff = None
    handler_path = None
    config = {
        'pdcupdater.fas': {
            'base_url': 'whatever',
            'username': 'whatever',
            'password': 'whatever',
        },
        'pdcupdater.koji_url': 'blahblahblah',
        'pdcupdater.old_composes_url': 'https://kojipkgs.fedoraproject.org/compose',
    }

    def setUp(self):
        if not self.handler_path:
            log.info("!! Warning - no handler path declared by base class.")

        config = BaseHandlerTest.config
        if self.handler_path:
            log.info("Initializing handler %s(%r)", self.handler_path, config)
            self.handler = fedmsg.utils.load_class(self.handler_path)(config)

        log.info("Setting up vcr cassette in %s", cassette_dir)
        filename = cassette_dir + self.id()
        self.vcr = vcr.use_cassette(filename, record_mode='new_episodes')
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
