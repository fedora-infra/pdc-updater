import logging
import logging.config

import fedmsg.config

import pdcupdater.handlers

log = logging.getLogger(__name__)

# https://github.com/product-definition-center/pdc-client/issues/8
try:
    import pdc_client
except ImportError:
    log.exception("No pdc_client available.")



def initialize():
    config = fedmsg.config.load_config()
    logging.config.dictConfig(config['logging'])
    pdc = pdc_client.PDCClient(**config['pdcupdater.pdc'])
    handlers = pdcupdater.handlers.load_handlers(config)
    for handler in handlers:
        log.info("Calling .initialize() on %r" % handler)
        pdc.set_comment("Initialized via %r" % handler)
        handler.initialize(pdc)


def audit():
    config = fedmsg.config.load_config()
    logging.config.dictConfig(config['logging'])
    pdc = pdc_client.PDCClient(**config['pdcupdater.pdc'])
    raise NotImplementedError()
