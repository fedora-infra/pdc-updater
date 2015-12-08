import logging
import logging.config

import fedmsg.config

import pdcupdater.handlers
import beanbag.bbexcept

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
    pdc.set_comment("Initialized by pdc-updater.")
    initialize_basics(pdc)
    handlers = pdcupdater.handlers.load_handlers(config)
    for handler in handlers:
        log.info("Calling .initialize() on %r" % handler)
        pdc.set_comment("Initialized via %r" % handler)
        try:
            handler.initialize(pdc)
        except beanbag.bbexcept.BeanBagException as e:
            log.exception(e.response.text)
            #raise  # TODO - eventually raise here.  While in dev, leave it out


def initialize_basics(pdc):
    """ Gotta have these before we can really do anything... """
    arches = [dict(name=name) for name in ["armhfp", "i386", "x86_64"]]
    pdc_arches = list(pdc_client.get_paged(pdc['arches']._))
    for arch in arches:
        if arch not in pdc_arches:
            log.info("Creating arch %r." % arch['name'])
            pdc['arches']._(arch)




def audit():
    config = fedmsg.config.load_config()
    logging.config.dictConfig(config['logging'])
    pdc = pdc_client.PDCClient(**config['pdcupdater.pdc'])
    raise NotImplementedError()
