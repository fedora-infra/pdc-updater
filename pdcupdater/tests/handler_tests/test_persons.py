import mock

import pdcupdater.utils
from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)


class TestNewPerson(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.persons:NewPersonHandler'
    config = {}

    def test_cannot_handle_fedbadges(self):
        idx = '2015-6c98c8e3-0dcb-497d-a0d8-0b3d026a4cfb'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, False)

    def test_can_handle_fas_new_person(self):
        idx = '2015-b456fe4e-6dff-431a-9116-280064fe6087'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, True)

    @mock_pdc
    def test_handle_new_package(self, pdc):
        idx = '2015-b456fe4e-6dff-431a-9116-280064fe6087'
        msg = pdcupdater.utils.get_fedmsg(idx)
        self.handler.handle(pdc, msg)
        self.assertDictEqual(pdc.calls, {
            'persons': [
                ('POST', dict(
                    username='alvicler',
                    email='alvicler@fedoraproject.org',
                )),
            ],
        })

    @mock_pdc
    @mock.patch('pdcupdater.services.fas_persons')
    def test_initialize_from_fas(self, pdc, fas):
        # Mock out FAS results
        fas.return_value = [
            {'username': 'ralph'},
            {'username': 'lmacken'},
        ]

        # Call the initializer
        self.handler.initialize(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'persons': [
                ('POST', dict(
                    username='ralph',
                    email='ralph@fedoraproject.org',
                )),
                ('POST', dict(
                    username='lmacken',
                    email='lmacken@fedoraproject.org',
                )),
            ],
        })

    @mock_pdc
    @mock.patch('pdcupdater.services.fas_persons')
    def test_audit_simple(self, pdc, fas):
        # Mock out FAS results
        fas.return_value = [
            {'username': 'ralph'},
            {'username': 'lmacken'},
        ]

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'persons': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        self.assertSetEqual(present, set())
        self.assertSetEqual(absent, set())

    @mock_pdc
    @mock.patch('pdcupdater.services.fas_persons')
    def test_audit_with_an_extra(self, pdc, fas):
        # Mock out FAS results
        fas.return_value = [
            {'username': 'ralph'},
        ]

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'persons': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        self.assertSetEqual(present, set(['lmacken']))
        self.assertSetEqual(absent, set())

    @mock_pdc
    @mock.patch('pdcupdater.services.fas_persons')
    def test_audit_missing_one(self, pdc, fas):
        # Mock out FAS results
        fas.return_value = [
            {'username': 'ralph'},
            {'username': 'lmacken'},
            {'username': 'toshio'},
        ]

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'persons': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        self.assertSetEqual(present, set())
        self.assertSetEqual(absent, set(['toshio']))

    @mock_pdc
    @mock.patch('pdcupdater.services.fas_persons')
    def test_audit_flipping_out(self, pdc, fas):
        # Mock out FAS results
        fas.return_value = [
            {'username': 'toshio'},
        ]

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'persons': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        self.assertSetEqual(present, set(['lmacken', 'ralph']))
        self.assertSetEqual(absent, set(['toshio']))
