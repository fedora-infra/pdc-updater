import logging
import logging.config
import sys

import fedmsg.config

import pdcupdater.handlers
import beanbag.bbexcept

log = logging.getLogger(__name__)

# https://github.com/product-definition-center/pdc-client/issues/8
import pdc_client


def _initialize_basics(pdc):
    """ Gotta have these before we can really do anything... """
    arches = [dict(name=name) for name in ["armhfp", "i386", "x86_64"]]
    pdc_arches = list(pdc_client.get_paged(pdc['arches']._))
    for arch in arches:
        if arch not in pdc_arches:
            log.info("Creating arch %r." % arch['name'])
            pdc['arches']._(arch)


def initialize():
    config = fedmsg.config.load_config()
    logging.config.dictConfig(config['logging'])
    pdc = pdc_client.PDCClient(**config['pdcupdater.pdc'])
    pdc.set_comment("Initialized by pdc-updater.")
    _initialize_basics(pdc)
    handlers = pdcupdater.handlers.load_handlers(config)
    for handler in handlers:
        log.info("Calling .initialize() on %r" % handler)
        pdc.set_comment("Initialized via %r" % handler)
        try:
            handler.initialize(pdc)
        except beanbag.bbexcept.BeanBagException as e:
            log.exception(e.response.text)
            #raise  # TODO - eventually raise here.  While in dev, leave it out


def audit():
    config = fedmsg.config.load_config()
    logging.config.dictConfig(config['logging'])
    pdc = pdc_client.PDCClient(**config['pdcupdater.pdc'])
    handlers = pdcupdater.handlers.load_handlers(config)

    results = {}
    for handler in handlers:
        results[type(handler).__name__] = handler.audit(pdc)

    retval = _print_audit_report(results)
    sys.exit(retval)

def _print_audit_report(results):
    fail = False
    for key, values in results.items():
        present, absent = values
        fail = fail or (not present and not absent)

    if fail:
        print "OK"
    else:
        print "WARN"

    print
    print "Summary"
    print "======="
    print

    for key, values in results.items():
        present, absent = values
        if not present and not absent:
            print "- [x]", key
        else:
            print "- [!]", key
            print "     ", len(present), "extra entries in PDC unaccounted for"
            print "     ", len(absent), "entries absent from PDC"

    print
    print "Details"
    print "======="

    for key, values in results.items():
        present, absent = values
        if not present and not absent:
            continue

        print
        print key
        print "-" * len(key)
        print

        if not present:
            print "No extra entries in PDC that do not appear in the source."
        else:
            print "Values present in PDC but missing from the source:"
            print
            for value in present:
                print "-", value

        print

        if not absent:
            print "No entries found in the source to be absent from from PDC."
        else:
            print "Values absent from PDC but present in the source:"
            print
            for value in absent:
                print "-", value

    if not fail:
        return 0
    else:
        return 2  # nagios "WARN" status code
