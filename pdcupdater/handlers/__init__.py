import abc

import fedmsg.utils


def load_handlers(config):
    """ Import and instantiate all handlers listed in the given config. """
    for import_path in config['pdcupdater.handlers']:
        cls = fedmsg.utils.load_class(import_path)
        handler = cls(config)
        yield handler


class BaseHandler(object):
    """ An abstract base class for handlers to enforce API. """
    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        self.config = config

    def construct_topics(self, config):
        # Don't use the environment when using STOMP
        if config.get('stomp_uri'):
            return [
                '.'.join([config['topic_prefix'], topic])
                for topic in self.topic_suffixes
            ]
        else:
            return [
                '.'.join([config['topic_prefix'], config['environment'],
                          topic])
                for topic in self.topic_suffixes
            ]

    @abc.abstractproperty
    def topic_suffixes(self):
        pass

    @abc.abstractmethod
    def can_handle(self, pdc, msg):
        """ Return True or False if this handler can handle this message. """
        pass

    @abc.abstractmethod
    def handle(self, pdc, msg):
        """ Handle a fedmsg and update PDC if necessary. """
        pass

    @abc.abstractmethod
    def audit(self, pdc):
        """ This is intended to be called from a cronjob once every few days
        and is meant to (in a read-only fashion) check that what PDC thinks is
        true about a service, is actually true.

        It is expected to take a long time to run.

        It should return a two lists.  The first should be a list of items
        present in PDC but not in the other service.  The second should be a
        list of items present in the other service, but not in PDC. Those lists
        will be sewn together into an email to the releng group.
        """
        pass

    @abc.abstractmethod
    def initialize(self, pdc):
        """ This needs to be called only once when pdc-updater is first
        installed.  It should query the original data source and initialize PDC
        with a base layer of data.

        It is expected to take a very long time to run.
        """
        pass
