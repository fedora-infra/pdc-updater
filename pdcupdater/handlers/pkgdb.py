import pdcupdater.handlers

class NewPackageHandler(pdcupdater.handlers.BaseHandler):
    """ When a new package gets added to pkgdb. """

    def can_handle(self, msg):
        raise NotImplementedError()

    def handle(self, pdc, msg):
        raise NotImplementedError()

    def audit(self):
        raise NotImplementedError()

    def initialize(self):
        raise NotImplementedError()
