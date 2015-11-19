import abc

import logging
log = logging.getLogger(__name__)


class AbstractPDCBase(object):
    """ An abstract base class that we use to construct a Mock for testing.

    Every method here should accept a fedmsg msg_id as the first argument.
    We'll use that to attach a PDC-Change-Comment header to every PDC request
    with a link to the originating event in datagrepper.  We can use that to
    build an audit trail to figure out what changed where and why.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        self.config = config

    @abc.abstractmethod
    def add_new_package(self, msg_id, name, branch):
        pass


class PDC(AbstractPDCBase):
    """ The real proxy class we use to interact with PDC.

    Still to be implemented.
    """

    # TODO -- use pdc_client for this
    # https://github.com/product-definition-center/pdc-client/issues/7
    # https://github.com/product-definition-center/pdc-client/issues/8
    pass
