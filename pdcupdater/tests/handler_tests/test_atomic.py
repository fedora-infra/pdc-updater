import os

import pdcupdater.utils
from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)

here = os.path.dirname(__file__)

class TestAtomicUpdate(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.atomic:AtomicComponentGroupHandler'
    config = {
    }

    def test_cannot_handle_other_git_push(self):
        idx = '2016-ab90226c-5fc3-48f8-83de-821e4fe0ade4'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, False)

    def test_can_handle_atomic_update_push(self):
        msg = {
            "topic": "org.fedoraproject.prod.trac.git.receive",
            "msg": {
                "commit": {
                    "branch": "master",
                    "repo": "fedora-atomic",
                },
            },
        }
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, True)

    @mock_pdc
    def test_handle_a_push(self, pdc):
        msg = {
            "topic": "org.fedoraproject.prod.trac.git.receive",
            "msg": {
                "commit": {
                    "branch": "master",
                    "repo": "fedora-atomic",
                },
            },
        }
        self.handler.handle(pdc, msg)

        # Check number of groups
        self.assertEquals(len(pdc.calls['component-group-types']), 4)
        self.assertEquals(len(pdc.calls['component-groups']), 8)
