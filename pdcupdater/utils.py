import copy
import contextlib
import functools
import itertools
import socket
import time

import requests
import six
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
    response = pdc['release-components']._(**query)
    if not response['count']:
        raise IndexError("No results found for %r after submitting %r" % (
            query, data))
    if response['count'] > 1:
        raise IndexError("%i results found for %r after submitting %r" % (
            response['count'], query, data))
    return response['results'][0]


def ensure_release_component_relationship_exists(pdc, parent, child, type):
    """ Create a release-component-relationship in PDC
    only if it doesn't already exist.
    """

    try:
        # Try to create it
        data = {
            'from_component': dict(id=parent['id']),
            'to_component': dict(id=child['id']),
            # This may not exist, and we have no API to create it.  It must be
            # entered by an admin in the admin panel beforehand.
            'type': type,
        }
        pdc['release-component-relationships']._(data)
    except beanbag.bbexcept.BeanBagException as e:
        if e.response.status_code != 400:
            raise
        body = e.response.json()
        if not 'non_field_errors' in body:
            raise

        message = u'The fields relation_type, from_component, to_component must make a unique set.'
        if body['non_field_errors'] != [message]:
            raise


def delete_bulk_release_component_relationships(pdc, parent, relationships):

    release = parent['release']
    if not isinstance(release, six.string_types):
        release = release['release_id']

    # Split things up by relationship type into a lookup keyed by type
    relationships = list(relationships)
    relationship_types = set([relation for relation, child in relationships])
    relationship_lookup = dict([
        (key, [child for relation, child in relationships if relation == key])
        for key in relationship_types
    ])

    for relationship_type, children in relationship_lookup.items():
        # Check to see if all the relations are all already there, first.
        query_kwargs = dict(
            from_component_name=parent['name'],
            from_component_release=release,
            type=relationship_type,
            to_component_name=children,
        )
        endpoint = pdc['release-component-relationships']._
        response = endpoint(**query_kwargs)

        # Nobody can ask us to delete things that aren't there.
        # That's unreasonable.  Sanity check.
        message = "%r != %r" % (response['count'], len(children))
        assert response['count'] == len(children), message

        # Find the primary keys for all of these...
        query = pdc.get_paged(endpoint, **query_kwargs)
        identifiers = [relation['id'] for relation in query]

        # Issue the DELETE request for those found primary keys.
        log.info("Pruning %i old relationships." % len(identifiers))
        endpoint("DELETE", identifiers)


def _chunked_iter(iterable, N):
    """ Yield successive N-sized chunks from an iterable. """
    for i in xrange(0, len(iterable), N):
        yield iterable[i: i + N]


def _chunked_query(pdc, endpoint, kwargs, key, iterable, count=False, N=100):
    """ Break up a large PDC query and return consolidated results.

    Given a query to PDC with a large iterable key, break that query into
    chunks of size N each.  The results are recombined and returned.  If
    `count` is `True`, then just the count is returned, otherwise, all the
    paged results are returned.

    See https://github.com/product-definition-center/product-definition-center/issues/421
    """

    # Set up our initial value as one of two different kinds of results
    result = []
    if count:
        result = 0

    # Copy our given kwargs so we don't modify them for our caller.
    kwargs = copy.copy(kwargs)

    # Step through our given iterable in chunks and make successive queries.
    for chunk in _chunked_iter(iterable, N):
        kwargs[key] = chunk
        if count:
            result = result + endpoint(**kwargs)['count']
        else:
            result = itertools.chain(result, pdc.get_paged(endpoint, **kwargs))

    return result


def ensure_bulk_release_component_relationships_exists(pdc, parent,
                                                       relationships,
                                                       component_type):
    release = parent['release']
    if not isinstance(release, six.string_types):
        release = release['release_id']

    # Split things up by relationship type into a lookup keyed by type
    relationships = list(relationships)
    relationship_types = set([relation for relation, child in relationships])
    relationship_lookup = dict([
        (key, [child for relation, child in relationships if relation == key])
        for key in relationship_types
    ])

    for relationship_type, children in relationship_lookup.items():
        # Check to see if all the relations are all already there, first.
        endpoint = pdc['release-component-relationships']._
        query_kwargs = dict(
            from_component_name=parent['name'],
            from_component_release=release,
            type=relationship_type,
        )
        count = _chunked_query(
            pdc, endpoint, query_kwargs,
            key='to_component_name', iterable=children,
            count=True)

        log.info("Of %i needed %s relationships in koji, found %i in PDC."
                 "  (%i are missing)" % (len(children), relationship_type,
                                         count, len(children) - count))

        if count != len(children):
            # If they weren't all there already, figure out which ones are missing.
            query = _chunked_query(
                pdc, endpoint, query_kwargs,
                key='to_component_name', iterable=children)
            present = [relation['to_component']['name'] for relation in query]
            absent_names = [name for name in children if name not in present]

            # This creates the components themselves if they are missing, but
            # importantly it also retrieves the primary key ids which we need
            # in the next step.
            absent = list(ensure_bulk_release_components_exist(
                pdc, release, absent_names, component_type=component_type))

            if len(absent) != len(children) - count:
                raise ValueError("Found that %i != %i" % (
                    len(absent), len(children) - count))

            # Make sure this guy exists and has a primary key id.
            if 'id' not in parent:
                parent = ensure_release_component_exists(
                    pdc, release, parent['name'], component_type)

            # Now issue a bulk create the missing ones.
            pdc['release-component-relationships']._([dict(
                from_component=dict(id=parent['id']),
                to_component=dict(id=child['id']),
                type=relationship_type,
            ) for child in absent])


def ensure_bulk_release_components_exist(pdc, release, components,
                                         component_type):

    ensure_bulk_global_components_exist(pdc, components)

    query_kwargs = dict(release=release, name=components, type=component_type)
    response = pdc['release-components']._(**query_kwargs)

    if response['count'] != len(components):
        # If they weren't all there already, figure out which ones are missing.
        query = pdc.get_paged(pdc['release-components']._, **query_kwargs)
        present = [component['name'] for component in query]
        absent = [name for name in components if name not in present]

        # Now issue a bulk create the missing ones.
        log.info("Of %i needed, %i release-components missing." % (
            len(components), len(absent)))
        pdc['release-components']._([dict(
            name=name,
            global_component=name,
            release=release,
            type=component_type
        ) for name in absent])

    # Finally, return all of the present components (with all of their primary
    # key IDs which were assigned server side.  that's why we have to query a
    # second time here....)
    return pdc.get_paged(pdc['release-components']._, **query_kwargs)


def ensure_bulk_global_components_exist(pdc, components):
    response = pdc['global-components']._(name=components)

    if response['count'] != len(components):
        # If they weren't all there already, figure out which ones are missing.
        query = pdc.get_paged(pdc['global-components']._, name=components)
        present = [component['name'] for component in query]
        absent = [name for name in components if name not in present]

        # Now issue a bulk create the missing ones.
        log.info("Of %i needed, %i global-components missing." % (
            len(components), len(absent)))
        pdc['global-components']._([dict(name=name) for name in absent])


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


def retry(timeout=500, interval=20, wait_on=Exception):
    """ A decorator that allows to retry a section of code...
    ...until success or timeout.
    """
    def wrapper(function):
        @functools.wraps(function)
        def inner(*args, **kwargs):
            start = time.time()
            while True:
                if (time.time() - start) >= timeout:
                    raise  # This re-raises the last exception.
                try:
                    return function(*args, **kwargs)
                except wait_on as e:
                    log.warn("Exception %r raised from %r.  Retry in %rs" % (
                        e, function, interval))
                    time.sleep(interval)
        return inner
    return wrapper
