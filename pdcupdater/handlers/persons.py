import pdcupdater.handlers


class NewPersonHandler(pdcupdater.handlers.BaseHandler):
    """ When a new person gets added to FAS. """

    def can_handle(self, msg):
        return msg['topic'].endswith('fas.user.create')

    def handle(self, pdc, msg):
        username = msg['msg']['user']
        email = '%s@fedoraproject.org' % username
        pdc['persons']._(dict(username=username, email=email))

    def audit(self):
        raise NotImplementedError()

    def initialize(self):
        raise NotImplementedError()
