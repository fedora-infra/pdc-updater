import abc


def PDC(config):
    """ Initialize our PDC controller from config. """
    if config.get('development-mode'):
        return PDCMock(config)
    else:
        return PDCProxy(config)


class PDCBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def no_clue_what_this_should_do(self):
        pass


class PDCMock(PDCBase):
    """ A fake PDC class used for testing. """
    pass


class PDCProxy(PDCBase):
    """ The real proxy class we use to interact with PDC. """
    pass
