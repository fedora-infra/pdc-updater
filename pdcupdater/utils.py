import copy
import contextlib

import requests
import beanbag.bbexcept

import logging
log = logging.getLogger(__name__)


def ensure_component_group_exists(pdc, component_group):
    """ Create a component_group in PDC if it doesn't already exist. """
    component_group_type = component_group['group_type']
    ensure_component_group_type_exists(pdc, component_group_type)
    try:
        # Try to create it
        pdc['component-groups']._(component_group)
    except beanbag.bbexcept.BeanBagException as e:
        if e.response.status_code != 400:
            raise
        body = e.response.json()
        if not 'non_field_errors' in body:
            raise
        message = u'The fields group_type, release, description must make a unique set.'
        if body['non_field_errors'] != [message]:
            raise


def ensure_component_group_type_exists(pdc, component_group_type):
    """ Create a component_group-type in PDC if it doesn't already exist. """
    try:
        # Try to create it
        pdc['component-group-types']._(dict(name=component_group_type))
    except beanbag.bbexcept.BeanBagException as e:
        if e.response.status_code != 400:
            raise
        body = e.response.json()
        if not 'name' in body:
            raise
        if body['name'] != [u"This field must be unique."]:
            raise


def ensure_release_exists(pdc, release_id, release):
    """ Create a release in PDC if it doesn't already exist. """
    try:
        pdc['releases'][release_id]._()
    except beanbag.bbexcept.BeanBagException as e:
        if e.response.status_code != 404:
            raise
        log.warn("No release %r exists.  Creating." % release_id)

        release_payload = copy.copy(release)
        release_payload.update(dict(
            active=True,
        ))
        pdc['releases']._(release_payload)
        log.info("Created %r" % release_payload)


def ensure_global_component_exists(pdc, name):
    response = pdc['global-components']._(name=name)
    if not response['results']:
        log.warn("No global-component %r exists.  Creating." % name)
        pdc['global-components']._(dict(name=name))


def ensure_release_component_exists(pdc, release_id, name):
    """ Create a release-component in PDC if it doesn't already exist. """
    ensure_global_component_exists(pdc, name)
    try:
        # Try to create it
        pdc['release-components']._({
            'name': name,
            'global_component': name,
            'release': release_id,
        })
    except beanbag.bbexcept.BeanBagException as e:
        if e.response.status_code != 400:
            raise
        body = e.response.json()
        if not 'non_field_errors' in body:
            raise
        message = u'The fields release, name must make a unique set.'
        if body['non_field_errors'] != [message]:
            raise


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
