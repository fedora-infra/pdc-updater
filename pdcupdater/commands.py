import logging
import logging.config
import sys

import fedmsg.config
import fedmsg.encoding

import pdcupdater.handlers
import pdcupdater.utils

import beanbag.bbexcept

log = logging.getLogger(__name__)

# https://github.com/product-definition-center/pdc-client/issues/8
import pdc_client


def retry():
    config = fedmsg.config.load_config()
    logging.config.dictConfig(config['logging'])
    msg_ids = sys.argv[1:]
    if msg_ids:
        messages = [pdcupdater.utils.get_fedmsg(idx) for idx in msg_ids]
    else:
        log.info("No msg_ids supplied.  Reading message payload from stdin.")
        messages = [fedmsg.encoding.loads(sys.stdin.read())]

    pdc = pdc_client.PDCClient(**config['pdcupdater.pdc'])
    handlers = pdcupdater.handlers.load_handlers(config)
    for msg in messages:
        pdcupdater.utils.handle_message(pdc, handlers, msg, verbose=True)


def _initialize_basics(pdc):
    """ Gotta have these before we can really do anything... """
    arches = [dict(name=name) for name in ["armhfp", "i386", "x86_64"]]
    pdc_arches = list(pdc.get_paged(pdc['arches']._))
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
    log.info("Done initializing.")

def audit():
    config = fedmsg.config.load_config()
    logging.config.dictConfig(config['logging'])
    pdc = pdc_client.PDCClient(**config['pdcupdater.pdc'])
    handlers = pdcupdater.handlers.load_handlers(config)

    results = {}
    for handler in handlers:
        name = type(handler).__name__
        log.info('Performing audit for %s' % name)
        results[name] = handler.audit(pdc)

    verbose = False
    retval = _print_audit_report(results, verbose)
    sys.exit(retval)

def _print_audit_report(results, verbose):
    fail = False
    for key, values in results.items():
        present, absent = values
        fail = fail or present or absent

    if not fail:
        print "Everything seems to be OK."
    else:
        print "WARNING - audit script detected something is wrong."

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

    limit = 100
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
            if verbose or len(present) < limit:
                for value in present:
                    print "-", value
                    if isinstance(present, dict):
                        print " ", present[value]
            else:
                present = list(present)
                for value in present[:limit]:
                    print "-", value
                    if isinstance(present, dict):
                        print " ", present[value]
                print "- (plus %i more... truncated.)" % (len(present) - limit)
        print

        if not absent:
            print "No entries found in the source to be absent from from PDC."
        else:
            print "Values absent from PDC but present in the source:"
            print
            if verbose or len(absent) < limit:
                for value in absent:
                    print "-", value
                    if isinstance(absent, dict):
                        print " ", absent[value]
            else:
                absent = list(absent)
                for value in absent[:limit]:
                    print "-", value
                    if isinstance(absent, dict):
                        print " ", absent[value]
                print "- (plus %i more... truncated.)" % (len(absent) - limit)

    if not fail:
        return 0
    else:
        return 2  # nagios "WARN" status code
