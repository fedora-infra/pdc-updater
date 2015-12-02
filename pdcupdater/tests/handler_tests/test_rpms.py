import json
import mock

from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)

def mocked_koji_response(tag, url):
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
    }]

def mocked_koji_response_missing_one(tag, url):
    response = mocked_koji_response(tag, url)
    if tag == 'epel7':
        return response[:1]
    return response

def mocked_koji_response_adding_one(tag, url):
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
        }]
    else:
        return mocked_koji_response(tag, url)


class TestNewRPM(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.rpms:NewRPMHandler'
    config = {}

    def test_cannot_handle_fedbadges(self):
        idx = '2015-6c98c8e3-0dcb-497d-a0d8-0b3d026a4cfb'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, False)

    def test_cannot_handle_non_stable_or_rawhide_build(self):
        idx = '2015-bf628d37-11bf-4354-a628-b3abfea03ed7'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, False)

    def test_cannot_handle_non_primary_rawhide_build(self):
        idx = '2015-e398ba94-827a-4c97-ac4b-39e5a6028818'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, False)

    def test_can_handle_new_primary_rawhide_build(self):
        idx = '2015-c37d4607-e8de-4229-990a-981c40a9bb93'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, True)

    def test_can_handle_stable_update_tag(self):
        idx = '2015-19772dd8-21f4-4b25-a557-41d313a74a88'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, True)

    @mock_pdc
    def test_handle_new_primary_rawhide_build(self, pdc):
        idx = '2015-c37d4607-e8de-4229-990a-981c40a9bb93'
        msg = self.get_fedmsg(idx)
        self.handler.handle(pdc, msg)
        self.assertDictEqual(pdc.calls, {
            'rpms': [
                ('POST', {
                    "name": u"thunderbird",
                    "version": u"38.4.0",
                    "release": u"2.fc24",
                    "linked_releases": [
                        u'f24',
                    ],
                    # TODO -- these three are still really unhandled.
                    "epoch": 0,
                    "arch": u"src",
                    "srpm_name": "undefined...",
                }),
            ],
        })

    @mock_pdc
    def test_handle_new_stable_update_tag(self, pdc):
        idx = '2015-19772dd8-21f4-4b25-a557-41d313a74a88'
        msg = self.get_fedmsg(idx)
        self.handler.handle(pdc, msg)
        self.assertDictEqual(pdc.calls, {
            'rpms': [
                ('POST', {
                    "name": u"criu",
                    "version": u"1.6.1",
                    "release": u"1.fc22",
                    "linked_releases": [
                        u'f22',
                    ],
                    # TODO -- these three are still really unhandled.
                    "epoch": 0,
                    "arch": u"src",
                    "srpm_name": "undefined...",
                }),
            ],
        })

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_builds_in_tag')
    def test_initialize_from_koji(self, pdc, koji):
        koji.side_effect = mocked_koji_response

        # Call the initializer
        self.handler.initialize(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'rpms': [
                ('POST', [{
                    'name': 'dvisvgm',
                    'arch': 'src',
                    'epoch': None,
                    'version': '1.11',
                    'release': '1.el7',
                    "linked_releases": [
                        u'epel7',
                    ],

                    # TODO -- this is still really unhandled.
                    "srpm_name": "undefined...",
                }, {
                    'name': 'rubygem-jmespath-doc',
                    'arch': 'noarch',
                    'epoch': None,
                    'version': '1.1.3',
                    'release': '1.el7',
                    "linked_releases": [
                        u'epel7',
                    ],

                    # TODO -- this is still really unhandled.
                    "srpm_name": "undefined...",
                }]),
            ],
        })

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_builds_in_tag')
    def test_audit(self, pdc, koji):
        # Mock out koji response
        koji.side_effect = mocked_koji_response

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
    @mock.patch('pdcupdater.services.koji_builds_in_tag')
    def test_audit_missing_one(self, pdc, koji):
        # Mock out koji response
        koji.side_effect = mocked_koji_response_missing_one

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
            "epoch": None,
            "linked_releases": ["epel7"],
            "name": "rubygem-jmespath-doc",
            "release": "1.el7",
            "srpm_name": "undefined...",
            "version": "1.1.3",
        }, sort_keys=True)]))
        self.assertSetEqual(absent, set())

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_builds_in_tag')
    def test_audit_adding_one(self, pdc, koji):
        # Mock out koji response
        koji.side_effect = mocked_koji_response_adding_one

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
            "epoch": None,
            "linked_releases": ["f24"],
            "name": "rubygem-jmespath-doc",
            "release": "1.fc24",
            "srpm_name": "undefined...",
            "version": "1.1.3",
        }, sort_keys=True)]))
