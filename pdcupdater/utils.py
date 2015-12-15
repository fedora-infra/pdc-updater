import copy
import contextlib

import requests
import beanbag.bbexcept

import logging
log = logging.getLogger(__name__)


def ensure_release_exists(pdc, release_id, release):
    """ Create a release in PDC if it doesn't already exist. """
    try:
        pdc['releases'][release_id]._()
    except beanbag.bbexcept.BeanBagException as e:
        if e.response.status_code != 404:
            raise
        log.warn("No release %r exists.  Creating." % release_id)

        product = dict(
            name='Fedora',
            short='fedora',
            version='NEXT',
        )
        product_id = "{short}-{version}".format(**product)
        ensure_product_exists(pdc, product_id, product)

        release_payload = copy.copy(release)
        release_payload.update(dict(
            active=True,
            base_product=product_id,
        ))
        pdc['releases']._(release_payload)


def ensure_product_exists(pdc, product_id, product):
    """ Create a product in PDC if it doesn't already exist. """
    try:
        pdc['base-products'][product_id]._()
    except beanbag.bbexcept.BeanBagException as e:
        if e.response.status_code != 404:
            raise
        log.warn("No product %r exists.  Creating." % product_id)
        pdc['base-products']._(product)


def ensure_global_component_exists(pdc, name):
    response = pdc['global-components']._(name=name)
    if not response['results']:
        log.warn("No global-component %r exists.  Creating." % name)
        pdc['global-components']._(dict(name=name))


def compose_exists(pdc, compose_id):
    """ Return True if a compose exists in PDC.  False if not. """
    try:
        pdc['composes'][compose_id]._()
        return True
    except beanbag.bbexcept.BeanBagException as e:
        if e.response.status_code != 404:
            raise
        return False


def get_fedmsg(idx):
    url = 'https://apps.fedoraproject.org/datagrepper/id'
    response = requests.get(url, params=dict(id=idx))
    if not bool(response):
        raise IOError("Failed to talk to %r %r" % (response.url, response))
    return response.json()


@contextlib.contextmanager
def annotated(client, msg_id):
    client.set_comment(msg_id)
    try:
        yield client
    finally:
        client.set_comment('No comment.')


def handle_message(pdc, handlers, msg, verbose=False):
    idx, topic = msg['msg_id'], msg['topic']
    for handler in handlers:
        name = type(handler).__name__
        if not handler.can_handle(msg):
            if verbose:
                log.info("%s could not handle %s" % (name, idx))
            continue
        log.info("%s handling %s %s" % (name, idx, topic))
        with annotated(pdc, msg['msg_id']) as client:
            try:
                handler.handle(client, msg)
            except beanbag.bbexcept.BeanBagException as e:
                log.error(e.response.text)
                raise
