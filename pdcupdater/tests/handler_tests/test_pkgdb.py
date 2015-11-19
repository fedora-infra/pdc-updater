from pdcupdater.tests.handler_tests import BaseHandlerTest

class TestNewPackage(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.pkgdb:NewPackageHandler'
    config = {}

    def test_cannot_handle_fedbadges(self):
        idx = '2015-6c98c8e3-0dcb-497d-a0d8-0b3d026a4cfb'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, False)

    def test_cannot_handle_bodhi(self):
        idx = '2015-9045593c-7376-43e8-af15-dc4c3fadc1f5'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, False)

    def test_cannot_handle_pkgdb_new_branch(self):
        idx = '2015-fc7a1d4f-56d8-45d6-a780-b317f0033a16'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, False)

    def test_can_handle_pkgdb_new_package(self):
        idx = '2015-5affaacc-1539-4e4f-9a5c-5b3f5c7caccf'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, True)

    def test_handle_new_package(self):
        idx = '2015-5affaacc-1539-4e4f-9a5c-5b3f5c7caccf'
        msg = self.get_fedmsg(idx)
        self.handler.handle(self.pdc, msg)
        calls = self.pdc.add_new_package.calls
        self.assertEquals(len(calls), 1)
        args, kwargs = calls[0]
        self.assertEquals(args, tuple())
        self.assertDictEqual(kwargs, dict(
            msg_id=idx,
            name='perl-Lingua-Translit',
            branch='f23',
            # TODO - we may want to send more initial info to PDC
            # ... add it here.
        ))


class TestNewBranch(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.pkgdb:NewPackageBranchHandler'
    config = {}

    def test_can_handle_pkgdb_new_branch(self):
        idx = '2015-fc7a1d4f-56d8-45d6-a780-b317f0033a16'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, True)

    def test_cannot_handle_pkgdb_new_package(self):
        idx = '2015-5affaacc-1539-4e4f-9a5c-5b3f5c7caccf'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, False)

    def test_handle_new_package_branch(self):
        idx = '2015-fc7a1d4f-56d8-45d6-a780-b317f0033a16'
        msg = self.get_fedmsg(idx)
        self.handler.handle(self.pdc, msg)
        calls = self.pdc.add_new_package.calls
        self.assertEquals(len(calls), 1)
        args, kwargs = calls[0]
        self.assertEquals(args, tuple())
        self.assertDictEqual(kwargs, dict(
            msg_id=idx,
            name='perl-Lingua-Translit',
            branch='master',
            # TODO - we may want to send more initial info to PDC
            # ... add it here.
        ))
