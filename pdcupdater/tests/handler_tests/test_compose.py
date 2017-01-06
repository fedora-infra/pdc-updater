import copy
import json
import os

import mock

import pdcupdater.utils
from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)

here = os.path.dirname(__file__)

with open(here + '/data/composeinfo.json', 'r') as f:
    composeinfo = json.loads(f.read())
    composeinfo_modified = copy.copy(composeinfo)
    composeinfo_modified['payload']['release']['short'] = \
        composeinfo_modified['payload']['release']['short'].lower()

with open(here + '/data/images.json', 'r') as f:
    images = json.loads(f.read())

with open(here + '/data/rpms.json', 'r') as f:
    rpms = json.loads(f.read())


class TestNewCompose(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.compose:NewComposeHandler'
    config = {}

    def test_cannot_handle_fedbadges(self):
        idx = '2015-6c98c8e3-0dcb-497d-a0d8-0b3d026a4cfb'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, False)

    def test_cannot_handle_new_compose_start(self):
        # Read the docs and code about the message producer for more info
        # https://pagure.io/pungi/blob/master/f/doc/configuration.rst#_566
        # https://pagure.io/pungi/blob/master/f/bin/pungi-fedmsg-notification
        msg = dict(
            topic='org.fedoraproject.prod.pungi.compose.status.change',
            msg=dict(
                status='STARTED',
                compose_id='Fedora-24-20151130.n.2',
                location='http://kojipkgs.fedoraproject.org/compose//rawhide/'
                'Fedora-24-20151130.n.2/compose',
            ),
        )
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, False)

    def test_cannot_handle_new_compose_doomed(self):
        # Read the docs and code about the message producer for more info
        # https://pagure.io/pungi/blob/master/f/doc/configuration.rst#_566
        # https://pagure.io/pungi/blob/master/f/bin/pungi-fedmsg-notification
        msg = dict(
            topic='org.fedoraproject.prod.pungi.compose.status.change',
            msg=dict(
                status='DOOMED',
                compose_id='Fedora-24-20151130.n.2',
                location='http://kojipkgs.fedoraproject.org/compose//rawhide/'
                'Fedora-24-20151130.n.2/compose',
            ),
        )
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, False)

    def test_can_handle_new_compose_finish(self):
        # Read the docs and code about the message producer for more info
        # https://pagure.io/pungi/blob/master/f/doc/configuration.rst#_566
        # https://pagure.io/pungi/blob/master/f/bin/pungi-fedmsg-notification
        msg = dict(
            topic='org.fedoraproject.prod.pungi.compose.status.change',
            msg=dict(
                status='FINISHED',
                compose_id='Fedora-24-20151130.n.2',
                location='http://kojipkgs.fedoraproject.org/compose//rawhide/'
                'Fedora-24-20151130.n.2/compose',
            ),
        )
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, True)

    @mock_pdc
    def test_handle_new_compose(self, pdc):
        # Read the docs and code about the message producer for more info
        # https://pagure.io/pungi/blob/master/f/doc/configuration.rst#_566
        # https://pagure.io/pungi/blob/master/f/bin/pungi-fedmsg-notification
        msg = dict(
            topic='org.fedoraproject.prod.pungi.compose.status.change',
            msg=dict(
                status='FINISHED',
                compose_id='Fedora-24-20151130.n.2',
                location='http://kojipkgs.fedoraproject.org/compose//rawhide/'
                'Fedora-24-20151130.n.2/compose',
            ),
        )
        self.handler.handle(pdc, msg)

        # Check compose images
        compose_images = pdc.calls['compose-images']
        self.assertEquals(len(compose_images), 1)
        self.assertDictEqual(compose_images[0][1], dict(
            release_id='fedora-24',
            composeinfo=composeinfo_modified,
            image_manifest=images,
        ))
        # Check compose rpms
        compose_rpms = pdc.calls['compose-rpms']
        self.assertEquals(len(compose_rpms), 1)
        self.assertEquals(compose_rpms[0][1], dict(
            release_id='fedora-24',
            composeinfo=composeinfo_modified,
            rpm_manifest=rpms,
        ))

    @mock_pdc
    @mock.patch('pdcupdater.services.old_composes')
    def test_initialize_from_old_composes(self, pdc, old_composes):
        # Mock out kojipkgs results
        old_composes.return_value = [
            ('rawhide', 'Fedora-24-20151130.n.2',
             'https://kojipkgs.fedoraproject.org/compose/rawhide/Fedora-24-20151130.n.2',
             ),
        ]

        # Call the initializer
        self.handler.initialize(pdc)

        # Check compose images
        compose_images = pdc.calls['compose-images']
        self.assertEquals(len(compose_images), 1)
        self.assertDictEqual(compose_images[0][1], dict(
            release_id='fedora-24',
            composeinfo=composeinfo_modified,
            image_manifest=images,
        ))
        # Check compose rpms
        compose_rpms = pdc.calls['compose-rpms']
        self.assertEquals(len(compose_rpms), 1)
        self.assertEquals(compose_rpms[0][1], dict(
            release_id='fedora-24',
            composeinfo=composeinfo_modified,
            rpm_manifest=rpms,
        ))

    @mock_pdc
    @mock.patch('pdcupdater.services.old_composes')
    def test_audit_simple(self, pdc, old_composes):
        # Mock out kojipkgs results
        old_composes.return_value = [
            ('rawhide', 'Fedora-24-20151130.n.2',
             'https://kojipkgs.fedoraproject.org/compose/rawhide/Fedora-24-20151130.n.2',
             ),
        ]

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'composes': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        self.assertSetEqual(present, set())
        self.assertSetEqual(absent, set())

    @mock_pdc
    @mock.patch('pdcupdater.services.old_composes')
    def test_audit_missing_one(self, pdc, old_composes):
        # Mock out kojipkgs results
        old_composes.return_value = [
            ('rawhide', 'Fedora-24-20151130.n.2',
             'https://kojipkgs.fedoraproject.org/compose/rawhide/Fedora-24-20151130.n.2',
             ),
            ('rawhide', 'Fedora-24-20151130.n.3',
             'https://kojipkgs.fedoraproject.org/compose/rawhide/Fedora-24-20151130.n.3',
             ),
        ]

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'composes': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        self.assertSetEqual(present, set())
        self.assertSetEqual(absent, set(['Fedora-24-20151130.n.3']))
