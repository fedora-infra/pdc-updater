import abc

import logging
log = logging.getLogger(__name__)


class AbstractPDCBase(object):
    """ An abstract base class that we use to construct a Mock for testing. """
    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        self.config = config

    @abc.abstractmethod
    def add_new_package(self, name, branch):
        pass


class PDC(AbstractPDCBase):
    """ The real proxy class we use to interact with PDC.

    Still to be implemented.
    """

    # TODO -- use pdc_client for this
    # https://github.com/product-definition-center/pdc-client/issues/7
    # https://github.com/product-definition-center/pdc-client/issues/8
    pass
