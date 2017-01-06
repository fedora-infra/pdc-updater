import json
import mock

import pdcupdater.utils

from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)


def mocked_koji_from_build_criu(url, buildid):
    return {
        'epoch': None,
        'name': 'criu',
        'nvr': 'criu-1.6.1-1.fc22',
    }, ["criu-1.6.1-1.fc22.src.rpm"]


def mocked_koji_from_build_thunderbird(url, buildid):
    return {
        'epoch': None,
        'name': 'thunderbird',
        'nvr': 'thunderbird-38.4.0-2.fc24',
    }, [
        "mozilla-crashreporter-thunderbird-debuginfo-38.4.0-2.fc24.x86_64.rpm",
        "thunderbird-38.4.0-2.fc24.armv7hl.rpm",
        "thunderbird-38.4.0-2.fc24.src.rpm",
        "thunderbird-38.4.0-2.fc24.x86_64.rpm",
        "thunderbird-debuginfo-38.4.0-2.fc24.armv7hl.rpm",
        "thunderbird-debuginfo-38.4.0-2.fc24.x86_64.rpm",
        "thunderbird-lightning-gdata-38.4.01.9.0.3-2.fc24.armv7hl.rpm",
        "thunderbird-lightning-gdata-38.4.01.9.0.3-2.fc24.x86_64.rpm",
    ]


def mocked_koji_from_tag(url, tag):
    if tag != 'epel7':
        return []
    return [{
        'build_id': 698494,
        'name': 'dvisvgm',
        'arch': 'src',
        'buildtime': 1447252790,
        'id': 6979644,
        'epoch': None,
        'version': '1.11',
        'release': '1.el7',
        'buildroot_id': 4386200,
        'payloadhash': '46f384609c0db547753857d5b0476cae',
        'size': 841828,
        # Extracted from the associated build
        'srpm_name': 'dvisvgm',
    }, {
        'build_id': 696907,
        'name': 'rubygem-jmespath-doc',
        'arch': 'noarch',
        'buildtime': 1446997456,
        'id': 6968508,
        'epoch': None,
        'version': '1.1.3',
        'release': '1.el7',
        'buildroot_id': 4364114,
        'payloadhash': '6b98468f3efe29367c923c577861dec5',
        'size': 175000,
        # Extracted from the associated build
        'srpm_name': 'rubygem-jmespath',
        'srpm_nevra': 'rubygem-jmespath-1.1.3-1.el7',
    }]


def mocked_koji_from_tag_missing_one(url, tag):
    response = mocked_koji_from_tag(url, tag)
    if tag == 'epel7':
        return response[:1]
    return response


def mocked_koji_from_tag_adding_one(url, tag):
    if tag == 'f24':
        return [{
            'build_id': 696907,
            'name': 'rubygem-jmespath-doc',
            'arch': 'noarch',
            'buildtime': 1446997456,
            'id': 6968508,
            'epoch': None,
            'version': '1.1.3',
            'release': '1.fc24',
            'buildroot_id': 4364114,
            'payloadhash': '6b98468f3efe29367c923c577861dec5',
            'size': 175000,
            # Extracted from the associated build
            'srpm_name': 'rubygem-jmespath',
            'srpm_nevra': 'rubygem-jmespath-1.1.3-1.fc24',
        }]
    else:
        return mocked_koji_from_tag(url, tag)


class TestNewRPM(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.rpms:NewRPMHandler'
    config = {}

    def test_cannot_handle_fedbadges(self):
        idx = '2015-6c98c8e3-0dcb-497d-a0d8-0b3d026a4cfb'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, False)

    def test_cannot_handle_non_stable_or_rawhide_build(self):
        idx = '2015-bf628d37-11bf-4354-a628-b3abfea03ed7'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, False)

    def test_cannot_handle_non_primary_rawhide_build(self):
        idx = '2015-e398ba94-827a-4c97-ac4b-39e5a6028818'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, False)

    def test_can_handle_new_primary_rawhide_build(self):
        idx = '2015-c37d4607-e8de-4229-990a-981c40a9bb93'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, True)

    def test_can_handle_stable_update_tag(self):
        idx = '2015-19772dd8-21f4-4b25-a557-41d313a74a88'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, True)

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_rpms_from_build')
    def test_handle_new_primary_rawhide_build(self, pdc, koji):
        koji.side_effect = mocked_koji_from_build_thunderbird
        idx = '2015-c37d4607-e8de-4229-990a-981c40a9bb93'
        msg = pdcupdater.utils.get_fedmsg(idx)
        self.handler.handle(pdc, msg)
        self.assertDictEqual(pdc.calls, {
            'releases/fedora-24': [('GET', {})],
            'rpms': [
                ('POST', {
                    "name": "mozilla-crashreporter-thunderbird-debuginfo",
                    "version": "38.4.0",
                    "release": "2.fc24",
                    "linked_releases": [
                        'fedora-24',
                    ],
                    "epoch": 0,
                    "arch": "x86_64",
                    "srpm_name": "thunderbird",
                    "srpm_nevra": "thunderbird-38.4.0-2.fc24",
                }),
                ('POST', {
                    "name": "thunderbird",
                    "version": "38.4.0",
                    "release": "2.fc24",
                    "linked_releases": [
                        'fedora-24',
                    ],
                    "epoch": 0,
                    "arch": "armv7hl",
                    "srpm_name": "thunderbird",
                    "srpm_nevra": "thunderbird-38.4.0-2.fc24",
                }),
                ('POST', {
                    "name": "thunderbird",
                    "version": "38.4.0",
                    "release": "2.fc24",
                    "linked_releases": [
                        'fedora-24',
                    ],
                    "epoch": 0,
                    "arch": "src",
                    "srpm_name": "thunderbird",
                    "srpm_nevra": None,
                }),
                ('POST', {
                    "name": "thunderbird",
                    "version": "38.4.0",
                    "release": "2.fc24",
                    "linked_releases": [
                        'fedora-24',
                    ],
                    "epoch": 0,
                    "arch": "x86_64",
                    "srpm_name": "thunderbird",
                    "srpm_nevra": "thunderbird-38.4.0-2.fc24",
                }),
                ('POST', {
                    "name": "thunderbird-debuginfo",
                    "version": "38.4.0",
                    "release": "2.fc24",
                    "linked_releases": [
                        'fedora-24',
                    ],
                    "epoch": 0,
                    "arch": "armv7hl",
                    "srpm_name": "thunderbird",
                    "srpm_nevra": "thunderbird-38.4.0-2.fc24",
                }),
                ('POST', {
                    "name": "thunderbird-debuginfo",
                    "version": "38.4.0",
                    "release": "2.fc24",
                    "linked_releases": [
                        'fedora-24',
                    ],
                    "epoch": 0,
                    "arch": "x86_64",
                    "srpm_name": "thunderbird",
                    "srpm_nevra": "thunderbird-38.4.0-2.fc24",
                }),
                ('POST', {
                    "name": "thunderbird-lightning-gdata",
                    "version": "38.4.01.9.0.3",
                    "release": "2.fc24",
                    "linked_releases": [
                        'fedora-24',
                    ],
                    "epoch": 0,
                    "arch": "armv7hl",
                    "srpm_name": "thunderbird",
                    "srpm_nevra": "thunderbird-38.4.0-2.fc24",
                }),
                ('POST', {
                    "name": "thunderbird-lightning-gdata",
                    "version": "38.4.01.9.0.3",
                    "release": "2.fc24",
                    "linked_releases": [
                        'fedora-24',
                    ],
                    "epoch": 0,
                    "arch": "x86_64",
                    "srpm_name": "thunderbird",
                    "srpm_nevra": "thunderbird-38.4.0-2.fc24",
                }),
            ],
        })

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_rpms_from_build')
    def test_handle_new_stable_update_tag(self, pdc, koji):
        koji.side_effect = mocked_koji_from_build_criu

        idx = '2015-19772dd8-21f4-4b25-a557-41d313a74a88'
        msg = pdcupdater.utils.get_fedmsg(idx)
        self.handler.handle(pdc, msg)
        self.assertDictEqual(pdc.calls, {
            'releases/fedora-22-updates': [('GET', {})],
            'rpms': [
                ('POST', {
                    "name": "criu",
                    "version": "1.6.1",
                    "release": "1.fc22",
                    "linked_releases": [
                        'fedora-22-updates',
                    ],
                    "epoch": 0,
                    "arch": "src",
                    "srpm_name": "criu",
                    "srpm_nevra": None,
                }),
            ],
        })

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_rpms_in_tag')
    def test_initialize_from_koji(self, pdc, koji):
        koji.side_effect = mocked_koji_from_tag

        # Call the initializer
        self.handler.initialize(pdc)

        # Check the PDC calls..
        # One POST for each release (but we only have rpms for one)
        rpm_calls = pdc.calls['rpms']

        self.assertEqual(len(rpm_calls), 2)
        self.assertDictEqual(rpm_calls[0][1], {
            'name': 'dvisvgm',
            'arch': 'src',
            'epoch': 0,
            'version': '1.11',
            'release': '1.el7',
            "linked_releases": [
                'epel-7-updates',
            ],
            "srpm_name": "dvisvgm",
            "srpm_nevra": None,
        })
        self.assertDictEqual(rpm_calls[1][1], {
            'name': 'rubygem-jmespath-doc',
            'arch': 'noarch',
            'epoch': 0,
            'version': '1.1.3',
            'release': '1.el7',
            "linked_releases": [
                'epel-7-updates',
            ],
            "srpm_name": "rubygem-jmespath",
            "srpm_nevra": "rubygem-jmespath-1.1.3-1.el7",
        })

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_rpms_in_tag')
    def test_audit(self, pdc, koji):
        # Mock out koji response
        koji.side_effect = mocked_koji_from_tag

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'rpms': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        self.assertSetEqual(present, set())
        self.assertSetEqual(absent, set())

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_rpms_in_tag')
    def test_audit_missing_one(self, pdc, koji):
        # Mock out koji response
        koji.side_effect = mocked_koji_from_tag_missing_one

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'rpms': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        # We removed a build from koji, so it is erroneously "present" in PDC
        self.assertSetEqual(present, set([json.dumps({
            "arch": "noarch",
            "epoch": 0,
            "linked_releases": [
                "epel-7-updates",
            ],
            "name": "rubygem-jmespath-doc",
            "version": "1.1.3",
            "release": "1.el7",
            "srpm_name": "rubygem-jmespath",
            "srpm_nevra": "rubygem-jmespath-1.1.3-1.el7",
        }, sort_keys=True)]))
        self.assertSetEqual(absent, set())

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_rpms_in_tag')
    def test_audit_adding_one(self, pdc, koji):
        # Mock out koji response
        koji.side_effect = mocked_koji_from_tag_adding_one

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'rpms': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        self.assertSetEqual(present, set())
        # We added an extra koji build, so it is "absent" from PDC.
        self.assertSetEqual(absent, set([json.dumps({
            "arch": "noarch",
            "epoch": 0,
            "linked_releases": [
                u'fedora-24',
            ],
            "name": "rubygem-jmespath-doc",
            "version": "1.1.3",
            "release": "1.fc24",
            "srpm_name": "rubygem-jmespath",
            "srpm_nevra": "rubygem-jmespath-1.1.3-1.fc24",
        }, sort_keys=True)]))
