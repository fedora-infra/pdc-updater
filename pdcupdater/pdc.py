import abc
import contextlib

import logging
log = logging.getLogger(__name__)


# https://github.com/product-definition-center/pdc-client/issues/8
try:
    import pdc_client
except ImportError:
    log.exception("No pdc_client available.")


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

    def __init__(self, config):
        super(PDC, self).__init__(config)
        self.config = config
        self.client = pdc_client.PDCClient(**config)

    def add_new_package(self, msg_id, name, branch):
        # TODO - find the release
        # TODO - add a global component first
        global_component = 'does this need to be an id?  or a string?'
        release = 'does this need to be an id?  or a string?'
        # and then, add the release component
        data = dict(
            # required
            name=name,
            release=release,
            global_component=global_component,

            # optional
            dist_git_branch=branch,
            bugzilla_component=name,
            brew_package=name,
            active=True,
            type='srpm',
        )
        # https://pdc.fedorainfracloud.org/rest_api/v1/release-components/
        with self.set_msg_id(msg_id):
            self.client['release-components'].post(**data)
        raise NotImplementedError

    @contextlib.contextmanager
    def set_msg_id(self, msg_id):
        self.client.set_comment(msg_id)
        try:
            yield
        finally:
            self.client.set_comment('No comment.')
