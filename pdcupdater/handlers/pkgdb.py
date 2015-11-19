import pdcupdater.handlers

class NewPackageHandler(pdcupdater.handlers.BaseHandler):
    """ When a new package gets added to pkgdb. """

    def can_handle(self, msg):
        return msg['topic'].endswith('pkgdb.package.new')

    def handle(self, pdc, msg):
        pdc.add_new_package(
            name=msg['msg']['package_name'],
            branch=msg['msg']['package_listing']['collection']['branchname'],
        )

    def audit(self):
        raise NotImplementedError()

    def initialize(self):
        raise NotImplementedError()


class NewPackageBranchHandler(pdcupdater.handlers.BaseHandler):
    """ When a new package gets a new branch in pkgdb. """

    def can_handle(self, msg):
        return msg['topic'].endswith('pkgdb.package.branch.new')

    def handle(self, pdc, msg):
        pdc.add_new_package(
            name=msg['msg']['package_listing']['package']['name'],
            branch=msg['msg']['package_listing']['collection']['branchname'],
        )

    def audit(self):
        raise NotImplementedError()

    def initialize(self):
        raise NotImplementedError()
