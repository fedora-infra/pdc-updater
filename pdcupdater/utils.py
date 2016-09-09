import copy
import contextlib
import functools
import json
import socket

import requests
import beanbag.bbexcept

import logging
log = logging.getLogger(__name__)

import dogpile.cache
cache = dogpile.cache.make_region()
cache.configure('dogpile.cache.memory', expiration_time=300)

session = requests.Session()


def get_group_pk(pdc, target_group):
    """ Return the primary key int identifier for a component group. """
    # List all of our component groups
    groups = pdc.get_paged(pdc['component-groups']._)

    ignored_keys = ['components']
    for group in groups:
        # Iterate over them until we find "the one"
        if all([
            group[key] == target_group[key]
            for key in target_group
            if key not in ignored_keys
        ]):
            return group['id']

    # If we can't find it, then complain.
    raise ValueError("Could not find matching group for %r" % target_group)


def ensure_component_group_exists(pdc, component_group):
    """ Create a component_group in PDC if it doesn't already exist. """

    # Scrub our input
    if 'components' in component_group:
        component_group = copy.copy(component_group)
        del component_group['components']

    # Check that the type exists first...
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


def ensure_release_component_exists(pdc, release_id, name, type='rpm'):
    """ Create a release-component in PDC if it doesn't already exist. """
    ensure_global_component_exists(pdc, name)
    try:
        # Try to create it
        data = {
            'name': name,
            'global_component': name,
            'release': release_id,
            'type': type,
        }
        # If this works, then we return the primary key and other data.
        return pdc['release-components']._(data)
    except beanbag.bbexcept.BeanBagException as e:
        # If it failed, see what kind of failure it was.
        if e.response.status_code != 400:
            raise
        body = e.response.json()
        if not 'non_field_errors' in body:
            raise
        message = u'The fields release, name must make a unique set.'
        if body['non_field_errors'] != [message]:
            raise

    # But if it was just that the component already existed, then go back and
    # query for what we tried to submit (return the primary key)
    query = dict(name=name, release=release_id)
    results = pdc['release-components']._(**query)
    if not results:
        raise IndexError("No results found for %r after submitting %r" % (
            query, data))
    if len(results) > 1:
        raise IndexError("%i results found for %r after submitting %r" % (
            len(results), query, data))
    return results[0]


def ensure_release_component_relationship_exists(pdc, parent, child, type):
    """ Create a release-component-relationship in PDC
    only if it doesn't already exist.
    """

    ensure_release_component_exists(pdc, parent['release']['release_id'], parent['name'])
    ensure_release_component_exists(pdc, child['release']['release_id'], child['name'])

    try:
        # Try to create it
        pdc['release-component-relationships']._({
            'parent': parent,
            'child': child,
            # This may not exist, and we have no API to create it.  It must be
            # entered by an admin in the admin panel beforehand.
            'type': type,
        })
    except beanbag.bbexcept.BeanBagException as e:
        if e.response.status_code != 400:
            raise
        body = e.response.json()
        if not 'non_field_errors' in body:
            raise

        # TODO - look for any further special psuedo-error handling cases here.
        log.warn(json.dumps(body, indent=2))
        raise
        #message = u'The fields release, name must make a unique set.'
        #if body['non_field_errors'] != [message]:
        #    raise


def delete_release_component_relationship(pdc, parent, child, type):
    """ Delete a release-component-relationship in PDC """

    # First, make sure that it exists...
    entries = list(pdc.get_paged(
        pdc['release-component-relationships']._,
        from_component_name=parent['name'],
        from_component_release=parent['release'],
        type=type,
        to_component_name=child['name'],
        to_component_release=child['release'],
    ))
    if len(entries) != 1:
        raise ValueError("No unique relationship found for "
                         "%r -> %r -> %r.  Found %i." % (
                             parent, type, child, len(entries)))

    # But also, we needed the primary key in order to delete it.
    primary_key = entries[0]['id']

    # Issue the DELETE request.
    pdc['release-component-relationships'][primary_key]._("DELETE", {})


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
    response = session.get(url, params=dict(id=idx))
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


@cache.cache_on_arguments()
def bodhi_releases():
    # TODO -- get these releases from PDC, instead of from Bodhi
    url = 'https://bodhi.fedoraproject.org/releases'
    response = session.get(url, params=dict(rows_per_page=100))
    if not bool(response):
        raise IOError('Failed to talk to %r: %r' % (url, response))
    return response.json()['releases']


@cache.cache_on_arguments()
def rawhide_tag():
    # TODO - get this tag from PDC, instead of guessing from pkgdb
    url = 'https://admin.fedoraproject.org/pkgdb/api/collections/'
    response = session.get(url, params=dict(clt_status="Under Development"))
    if not bool(response):
        raise IOError('Failed to talk to %r: %r' % (url, response))
    collections = response.json()['collections']
    rawhide = [c for c in collections if c['koji_name'] == 'rawhide'][0]
    return 'f' + rawhide['dist_tag'].strip('.fc')


def interesting_tags():
    """ Returns a list of "interesting tags".

    Eventually, we should query PDC itself to figure out what tags we should be
    concerned with.
    """
    releases = bodhi_releases()
    stable_tags = [r['stable_tag'] for r in releases]
    return stable_tags + [rawhide_tag()]


def release2reponame(release):
    """ Convert a PDC release to an mdapi repo name lexicographically. """
    # TODO -- we should be able to do this by querying the pdc releases
    # themselves and getting a repo url and parsing that.
    if 'f' + release['version'] == rawhide_tag():
        return 'rawhide'
    if release['short'] == 'fedora':
        return 'f' + release['version']
    if release['name'] == 'EPEL':
        pass

def subpackage2parent(package, pdc_release):
    """ Use mdapi to return the parent package of a given subpackage """

    repo = release2reponame(pdc_release)
    url = 'https://apps.fedoraproject.org/mdapi/{repo}/pkg/{package}'
    url = url.format(repo=repo, package=package)
    response = session.get(url)
    if not bool(response):
        log.debug("Could not talk to mdapi %r %r" % (response.url, response))
        return package
    data = response.json()
    return data['basename']


def pkgdb2release(collection):
    if collection['branchname'] == 'master':
        return "fedora-" + collection['dist_tag'][-2:]
    release = collection['name'].lower().split()[-1:] + [collection['version']]
    if collection['status'] != 'Under Development':
        release += ['updates']
    return "-".join(release)


def tag2release(tag):
    if tag == rawhide_tag():
        release = {
            'name': 'Fedora',
            'short': 'fedora',
            'version': tag.strip('f'),
            'release_type': 'ga',
        }
        release_id = "{short}-{version}".format(**release)
    else:
        bodhi_info = {r['stable_tag']: r for r in bodhi_releases()}[tag]
        if 'EPEL' in bodhi_info['id_prefix']:
            release = {
                'name': 'Fedora EPEL',
                'short': 'epel',
                'version': bodhi_info['version'],
                'release_type': 'updates',
            }
        else:
            release = {
                'name': 'Fedora Updates',
                'short': 'fedora',
                'version': bodhi_info['version'],
                'release_type': 'updates',
            }
        release_id = "{short}-{version}-{release_type}".format(**release)

    return release_id, release


def with_ridiculous_timeout(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        original = socket.getdefaulttimeout()
        socket.setdefaulttimeout(600)
        try:
            return function(*args, **kwargs)
        finally:
            socket.setdefaulttimeout(original)
    return wrapper
