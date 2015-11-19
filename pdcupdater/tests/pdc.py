from pdcupdater.pdc import AbstractPDCBase

import logging
log = logging.getLogger(__file__)


class MockedMethod(object):
    calls = []
    return_value = None

    def __init__(self, method):
        self.method = method.__name__

    def __call__(self, *args, **kwargs):
        # Leave a note that we were called.
        self.calls.append((args, kwargs,))
        # Tell the world
        log.info("Called %s with (%r, %r)" % (self.method, args, kwargs))
        # And don't even bother calling the actual method.
        return self.return_value


def mocked(method):
    return MockedMethod(method)


class PDCMock(AbstractPDCBase):
    """ A fake PDC class used for testing. """
    def __init__(self, config):
        super(PDCMock, self).__init__(config)

        # Set this to an empty list every time we are initialized.
        for attr in dir(self):
            value = getattr(self, attr)
            if isinstance(value, MockedMethod):
                value.calls = []
                value.return_value = None

    @mocked
    def add_new_package(self, **kwargs):
        """ This never actually gets called. """
