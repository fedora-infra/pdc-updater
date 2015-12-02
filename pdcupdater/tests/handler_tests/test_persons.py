from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)


class TestNewPerson(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.persons:NewPersonHandler'
    config = {}

    def test_cannot_handle_fedbadges(self):
        idx = '2015-6c98c8e3-0dcb-497d-a0d8-0b3d026a4cfb'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, False)

    def test_can_handle_fas_new_person(self):
        idx = '2015-b456fe4e-6dff-431a-9116-280064fe6087'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, True)

    @mock_pdc
    def test_handle_new_package(self, pdc):
        idx = '2015-b456fe4e-6dff-431a-9116-280064fe6087'
        msg = self.get_fedmsg(idx)
        self.handler.handle(pdc, msg)
        self.assertDictEqual(pdc.calls, {
            'persons': [
                ('POST', dict(
                    username='alvicler',
                    email='alvicler@fedoraproject.org',
                )),
            ],
        })
