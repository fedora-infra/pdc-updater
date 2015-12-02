from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)


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
