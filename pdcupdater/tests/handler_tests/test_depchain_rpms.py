import json
import os

import mock

import pdcupdater.utils
import pdcupdater.handlers.depchain.rpms
from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)


def load_example_message(filename):
    here = os.path.dirname(__file__)
    with open(os.path.join(here, 'data', filename), 'rb') as f:
        return json.loads(f.read().decode('utf-8'))


def format_envelope(envelope):
    # Remove the envelope
    # https://github.com/mokshaproject/moksha/pull/35
    headers = envelope.get('headers', {})
    topic, msg = envelope['topic'], envelope['body']

    # Stuff topic and headers back into the message body, for convenience.
    msg['topic'] = topic
    msg['headers'] = headers
    return msg


class TestBuildtimeDepIngestion(BaseHandlerTest):
    maxDiff = None
    handler_path = 'pdcupdater.handlers.depchain.rpms:NewRPMBuildTimeDepChainHandler'
    config = {}

    @mock.patch('pdcupdater.utils.rawhide_tag')
    @mock.patch('pdcupdater.utils.interesting_tags')
    def test_can_handle_buildsys_tag_message(self, tags, rawhide):
        tags.return_value = ['f24']
        rawhide.return_value = 'f24'
        idx = '2016-662e75d1-5830-4c84-9855-fd07a3018f7a'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, True)

    def test_construct_topic_fedora_message(self):
        config = {
            'zmq_enabled': True,
            'environment': 'dev',
            'topic_prefix': 'org.fedoraproject'
        }
        result = self.handler.construct_topics(config)
        self.assertEqual(
            result,
            ['org.fedoraproject.dev.buildsys.tag',
             'org.fedoraproject.dev.brew.build.tag']
        )

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_list_buildroot_for')
    @mock.patch('pdcupdater.utils.rawhide_tag')
    @mock.patch('pdcupdater.utils.interesting_tags')
    def test_handle_new_build(self, pdc, tags, rawhide, buildroot):
        tags.return_value = ['f24']
        rawhide.return_value = 'f24'
        buildroot.return_value = [
            {'name': 'wat', 'is_update': True},
        ]

        idx = '2016-662e75d1-5830-4c84-9855-fd07a3018f7a'
        msg = pdcupdater.utils.get_fedmsg(idx)
        self.handler.handle(pdc, msg)
        expected_keys = [
            'release-component-relationships',
            'releases/fedora-24',
            'release-components',
            'global-components',
        ]
        self.assertEquals(pdc.calls.keys(), expected_keys)

        self.assertEqual(len(pdc.calls['global-components']), 22)
        self.assertEqual(len(pdc.calls['release-components']), 22)
        self.assertEqual(len(pdc.calls['release-component-relationships']), 66)

    @mock_pdc
    @mock.patch('pdcupdater.utils.rawhide_tag')
    @mock.patch('pdcupdater.utils.interesting_tags')
    @mock.patch('pdcupdater.services.koji_list_buildroot_for')
    @mock.patch('pdcupdater.services.koji_rpms_from_build')
    @mock.patch('pdcupdater.services.koji_rpms_in_tag')
    def test_audit_empty_koji(self, pdc, builds, rpms, buildroot, tags, rawhide):
        tags.return_value = ['f24']
        rawhide.return_value = 'f24'

        # Mock out koji results
        builds.return_value = [{
            'build_id': 'fake_build_id',
            'name': 'guake',
            'version': 1,
            'release': 2,
            'arch': 'foo',
        }]
        rpms.return_value = {}, []
        buildroot.return_value = []

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'release-component-relationships': [
                ('GET', {
                    'page': 1,
                    'from_component_release': 'fedora-24',
                    'type': 'RPMBuildRequires',
                }),
                ('GET', {
                    'page': 1,
                    'from_component_release': 'fedora-24',
                    'type': 'RPMBuildRoot',
                }),
            ],
            'releases/fedora-24': [('GET', {})]
        })

        # Check the results.
        self.assertSetEqual(present, set())
        self.assertSetEqual(absent, set())

    @mock_pdc
    @mock.patch('pdcupdater.utils.rawhide_tag')
    @mock.patch('pdcupdater.utils.interesting_tags')
    @mock.patch('pdcupdater.services.koji_list_buildroot_for')
    @mock.patch('pdcupdater.services.koji_rpms_from_build')
    @mock.patch('pdcupdater.services.koji_rpms_in_tag')
    def test_audit_mismatch(self, pdc, builds, rpms, buildroot, tags, rawhide):
        tags.return_value = ['f24']
        rawhide.return_value = 'f24'

        # Mock out koji results
        _build = {
            'build_id': 'fake_build_id',
            'name': 'guake',
            'version': 1,
            'release': 2,
            'arch': 'foo',
        }
        builds.return_value = [_build]
        rpms.return_value = _build, ['some rpm filename']
        buildroot.return_value = [
            { 'name': 'buildtimelib1', 'is_update': True, },
            { 'name': 'buildtimelib2', 'is_update': False, },
        ]

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'release-component-relationships': [
                ('GET', {
                    'page': 1,
                    'from_component_release': 'fedora-24',
                    'type': 'RPMBuildRequires',
                }),
                ('GET', {
                    'page': 1,
                    'from_component_release': 'fedora-24',
                    'type': 'RPMBuildRoot',
                }),
            ],
            'releases/fedora-24': [('GET', {})]
        })

        # Check the results.
        self.assertSetEqual(present, set([]))
        self.assertSetEqual(absent, set([
            'guake/fedora-24 RPMBuildRequires buildtimelib1/fedora-24',
            'guake/fedora-24 RPMBuildRoot buildtimelib2/fedora-24',
        ]))


class TestRuntimeDepIngestionFedora(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.depchain.rpms:NewRPMRunTimeDepChainHandler'
    config = {}

    @mock_pdc
    @mock.patch('pdcupdater.utils.rawhide_tag')
    @mock.patch('pdcupdater.utils.interesting_tags')
    @mock.patch('pdcupdater.services.koji_yield_rpm_requires')
    @mock.patch('pdcupdater.services.koji_rpms_from_build')
    @mock.patch('pdcupdater.services.koji_rpms_in_tag')
    def test_audit_mismatch(self, pdc, builds, rpms, requires, tags, rawhide):
        tags.return_value = ['f24']
        rawhide.return_value = 'f24'

        # Mock out koji results
        _build = {
            'build_id': 'fake_build_id',
            'name': 'guake',
            'version': 1,
            'release': 2,
            'arch': 'foo',
        }
        builds.return_value = [_build]
        rpms.return_value = _build, ['some rpm filename']
        requires.return_value = [
            ('runtimelib1', '', '',),
        ]

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'release-component-relationships': [ ('GET', {
                'page': 1, 'from_component_release': 'fedora-24', 'type': 'RPMRequires'
            })],
            'releases/fedora-24': [('GET', {})]
        })

        # Check the results.
        self.assertSetEqual(present, set(['guake/fedora-24 RPMRequires nethack/fedora-24']))
        self.assertSetEqual(absent, set(['guake/fedora-24 RPMRequires runtimelib1/fedora-24']))

    @mock_pdc
    @mock.patch('pdcupdater.utils.rawhide_tag')
    @mock.patch('pdcupdater.utils.interesting_tags')
    @mock.patch('pdcupdater.services.koji_yield_rpm_requires')
    @mock.patch('pdcupdater.services.koji_rpms_from_build')
    @mock.patch('pdcupdater.services.koji_rpms_in_tag')
    def test_audit_simple_match(self, pdc, builds, rpms, requires, tags, rawhide):
        tags.return_value = ['f24']
        rawhide.return_value = 'f24'

        # Mock out koji results
        _build = {
            'build_id': 'fake_build_id',
            'name': 'guake',
            'version': 1,
            'release': 2,
            'arch': 'foo',
        }
        builds.return_value = [_build]
        rpms.return_value = _build, ['some rpm filename']
        requires.return_value = [
            ('nethack', '', '',),
        ]

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'release-component-relationships': [ ('GET', {
                'page': 1, 'from_component_release': 'fedora-24', 'type': 'RPMRequires'
            })],
            'releases/fedora-24': [('GET', {})]
        })

        # Check the results.
        self.assertSetEqual(present, set())
        self.assertSetEqual(absent, set())

    @mock_pdc
    @mock.patch('pdcupdater.utils.rawhide_tag')
    @mock.patch('pdcupdater.utils.interesting_tags')
    @mock.patch('pdcupdater.services.koji_yield_rpm_requires')
    @mock.patch('pdcupdater.services.koji_rpms_from_build')
    @mock.patch('pdcupdater.services.koji_rpms_in_tag')
    def test_initialize(self, pdc, builds, rpms, requires, tags, rawhide):
        tags.return_value = ['f24']
        rawhide.return_value = 'f24'

        # Mock out koji results
        _build = {
            'build_id': 'fake_build_id',
            'name': 'guake',
            'version': 1,
            'release': 2,
            'arch': 'foo',
        }
        builds.return_value = [_build]
        rpms.return_value = _build, ['some rpm filename']
        requires.return_value = [
            ('nethack', '', '',),
        ]

        # Call the initializer
        self.handler.initialize(pdc)

        # Check the PDC calls..
        expected_calls = {
            'releases/fedora-24': [('GET', {}), ('GET', {})]
        }

        self.assertDictEqual(pdc.calls, expected_calls)


class FakeHandler(pdcupdater.handlers.depchain.rpms.BaseRPMDepChainHandler):
    managed_types = ('RPMBuildRequires', 'RPMBuildRoot')
    # The types of the parents and children in our managed relationships
    parent_type = 'rpm'
    child_type = 'rpm'

    def interesting_tags(self, pdc):
        return ['rhel-9000-candidate']

    def _yield_koji_relationships_from_build(self, url, build, rpms=None):
        yield 'wat', 'RPMBuildRequires', 'bar'


class TestRuntimeDepIngestionRedHat(BaseHandlerTest):
    handler_path = 'pdcupdater.tests.handler_tests.test_depchain_rpms:FakeHandler'
    config = {}

    def test_handle_brew_message(self):
        msg = load_example_message('messagebus-example1.json')
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, True)

    def test_construct_topic_brew_message(self):
        config = {
            'stomp_uri': 'message.example.local:61612',
            'zmq_enabled': False,
            'topic_prefix': '/queue/Consumer.pdc-updater.VirtualTopic.eng'
        }
        result = self.handler.construct_topics(config)
        self.assertEqual(
            result,
            ['/queue/Consumer.pdc-updater.VirtualTopic.eng.brew.build.tag']
        )

    def test_construct_topic_brew_message_zmq_enabled(self):
        config = {
            'stomp_uri': 'message.example.local:61612',
            'zmq_enabled': True,
            'topic_prefix': '/queue/Consumer.pdc-updater.VirtualTopic.eng'
        }
        try:
            self.handler.construct_topics(config)
        except Exception as e:
            self.assertEqual(type(e), Exception)
            self.assertEqual(
                e.message,
                'pdc-updater cannot support both STOMP and ZMQ being enabled'
            )

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_list_buildroot_for')
    @mock.patch('pdcupdater.utils.tag2release')
    @mock.patch('pdcupdater.utils.interesting_tags')
    def test_handle_new_brew_build(self, pdc, tags, tag2release, buildroot):
        tags.return_value = ['rhel-9000-candidate']
        tag2release.return_value = 'rhel-9000', {
        }
        buildroot.return_value = [
            {'name': 'wat', 'is_update': True},
        ]

        msg = format_envelope(load_example_message('messagebus-example1.json'))
        self.handler.handle(pdc, msg)
        expected_keys = [
            'release-component-relationships',
            'releases/rhel-9000',
            'release-components',
            'global-components',
        ]
        self.assertEquals(pdc.calls.keys(), expected_keys)

        self.assertEqual(len(pdc.calls['global-components']), 1)
        self.assertEqual(len(pdc.calls['release-components']), 1)
        self.assertEqual(len(pdc.calls['release-component-relationships']), 3)
