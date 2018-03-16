import copy
import contextlib
import functools
import socket
import time
import os
import shutil
import tempfile

import requests
import requests_kerberos
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
        if 'non_field_errors' not in body and 'detail' not in body:
            raise
        message = u'The fields group_type, release, description must make a unique set.'
        if body.get('non_field_errors') != [message] \
                and body.get('detail') != [message]:
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
        log.info("Creating release %r" % release_payload)
        pdc['releases']._(release_payload)


@cache.cache_on_arguments()
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
            'dist_git_branch': releaseid2branch(pdc, release_id),
            'type': type,
        }
        # If this works, then we return the primary key and other data.
        return pdc['release-components']._(data)
    except beanbag.bbexcept.BeanBagException as e:
        # If it failed, see what kind of failure it was.
        if e.response.status_code != 400:
            raise
        body = e.response.json()
        if 'non_field_errors' not in body and 'detail' not in body:
            raise
        allowable = [
            # This is the old error string
            u'The fields release, name must make a unique set.',
            # This is the new error string, after
            # https://github.com/product-definition-center/product-definition-center/pull/422
            u'The fields release, name, type must make a unique set.',
        ]
        # The old error message location
        if 'non_field_errors' in body and not any(
                [body.get('non_field_errors', []) == [s] for s in allowable]):
            raise
        # The new error message location
        # https://github.com/product-definition-center/product-definition-center/commit/a4b17981930760238e3e2a07c10022f019bf5cf2
        if 'detail' in body and not any(
                [body.get('detail', []) == [s] for s in allowable]):
            raise

    # But if it was just that the component already existed, then go back and
    # query for what we tried to submit (return the primary key)
    query = dict(name=name, release=release_id, type=type)
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
        if 'non_field_errors' not in body and 'detail' not in body:
            raise

        message = u'The fields relation_type, from_component, to_component must make a unique set.'
        if body.get('non_field_errors') != [message] \
                and body.get('detail') != [message]:
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

    endpoint = pdc['release-component-relationships']._

    for relationship_type, children in relationship_lookup.items():
        # Check to see if all the relations are all already there, first.
        query_kwargs = dict(
            from_component_name=parent['name'],
            from_component_release=release,
            type=relationship_type,
        )
        response = _get_existing_items(endpoint, children, query_kwargs, 'to_component', 'name')

        # Nobody can ask us to delete things that aren't there.
        # That's unreasonable.  Sanity check.
        message = "%r != %r" % (len(response), len(children))
        assert len(response) == len(children), message

        # Find the primary keys for all of these...
        query = pdc.get_paged(endpoint, **query_kwargs)
        identifiers = [relation['id'] for relation in query]

        # Issue the DELETE request for those found primary keys.
        log.info("Pruning %i old relationships." % len(identifiers))
        endpoint("DELETE", identifiers)


def _get_absent_items(endpoint, items, query_kwargs, field_name, sub_field_name=None):
    present = _get_existing_items(endpoint, items, query_kwargs, field_name, sub_field_name)
    return set(items) - present


def _get_existing_items(endpoint, items, query_kwargs, field_name, sub_field_name=None):
    query = endpoint.results(fields=field_name, page_size=-1, **query_kwargs)
    return {item[field_name][sub_field_name] if sub_field_name else item[field_name] for item in query}


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
        (key, set([child for relation, child in relationships if relation == key]))
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
        absent_names = _get_absent_items(endpoint, children, query_kwargs, 'to_component', 'name')
        count = len(absent_names)

        log.info("Of %i needed %s relationships for %s in koji, found %i in PDC."
                 "  (%i are missing)" % (
                     len(children), relationship_type,
                     parent['name'], count,
                     len(children) - count))

        if absent_names:
            # This creates the components themselves if they are missing, but
            # importantly it also retrieves the primary key ids which we need
            # in the next step.
            absent = ensure_bulk_release_components_exist(
                pdc, release, absent_names, component_type=component_type)

            #if len(absent) != len(absent_names):
            #    raise ValueError("Error1 creating components: %i != %i" % (
            #        len(absent), len(absent_names)))

            #if len(absent) != len(children) - count:
            #    raise ValueError("Error2 creating components: %i != %i" % (
            #        len(absent), len(children) - count))

            # Make sure this guy exists and has a primary key id.
            if 'id' not in parent:
                parent = ensure_release_component_exists(
                    pdc, release, parent['name'], component_type)

            # Now issue a bulk create the missing ones.
            endpoint([dict(
                from_component=dict(id=parent['id']),
                to_component=dict(id=child['id']),
                type=relationship_type,
            ) for child in absent])


def ensure_bulk_release_components_exist(pdc, release, components,
                                         component_type):

    ensure_bulk_global_components_exist(pdc, components)

    endpoint = pdc['release-components']._
    query_kwargs = dict(release=release, type=component_type)
    absent = _get_absent_items(endpoint, components, query_kwargs, 'name')

    if absent:
        ## Validate that.
        #if len(absent) != len(components) - count:
        #    raise ValueError("Error creating components: %i != (%i - %i)" % (
        #        len(absent), len(components), count))

        # Now issue a bulk create the missing ones.
        log.info("Of %i needed, %i release-components missing." % (
            len(components), len(absent)))
        endpoint([dict(
            name=name,
            global_component=name,
            release=release,
            type=component_type
        ) for name in absent])

    # Finally, return all of the present components (with all of their primary
    # key IDs which were assigned server side.  that's why we have to query a
    # second time here....). The retry decorator is to compensate for a bug in
    # PDC which returns an HTTP status code before it's done writing to the
    # database
    @retry(timeout=300, interval=10, wait_on=AssertionError)
    def get_present_components():
        results = _get_existing_items(endpoint, components, query_kwargs, 'name')
        assert len(results) == len(components)
        return results

    return get_present_components()


def ensure_bulk_global_components_exist(pdc, components):
    endpoint = pdc['global-components']._
    absent = _get_absent_items(endpoint, components, {}, 'name')

    if absent:
        # Now issue a bulk create the missing ones.
        log.info("Of %i needed, %i global-components missing." % (
            len(components), len(absent)))
        endpoint([dict(name=name) for name in absent])


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
    debug = log.info if verbose else log.debug
    idx, topic = msg['msg_id'], msg['topic']
    for handler in handlers:
        name = type(handler).__name__
        if not handler.can_handle(pdc, msg):
            debug("%s could not handle %s" % (name, idx))
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


def interesting_container_tags():
    """ Returns a list of "interesting tags" relevant to containers.

    Eventually, we should query PDC itself to figure out what tags we should be
    concerned with.
    """
    tags = interesting_tags()

    suffix = '-updates'
    for i, tag in enumerate(tags):
        if tag.endswith(suffix):
            tags[i] = tag[:-len(suffix)]

    tags = [tag for tag in tags if '-' not in tag]

    return ['%s-docker' % tag for tag in tags] + \
        ['%s-container' % tag for tag in tags]


@cache.cache_on_arguments()
def all_tags_from_pdc(pdc):
    """ Return a list of allowed tags from all active PDC releases. """
    results = set()
    for release in pdc.get_paged(pdc['releases']._, active=True):
        brew_data = release.get('brew') or {}
        for tag in brew_data.get('allowed_tags', []):
            results.add(tag)
    return results


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


@cache.cache_on_arguments()
def releaseid2branch(pdc, release_id):
    """ Convert a PDC release_id to a dist-git branch name.

    May return `None` if we don't know.
    """
    release = pdc['releases'][release_id]._()
    # May return `None` if undefined.
    return (release.get('dist_git') or {}).get('branch')


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


def tag2release(tag, pdc=None):
    if pdc:
        return _tag2release_with_pdc(pdc, tag)
    else:
        return _tag2release_fedora(tag)


def _tag2release_with_pdc(pdc, tag):
    """ Use PDC to figure out what release is associated with this tag. """
    releases = list(pdc.get_paged(
        pdc['releases']._,
        brew_allowed_tag=tag,
    ))

    if not releases:
        raise ValueError("Could not find matching release for tag %r" % tag)

    if len(releases) != 1:
        log.error("%i different releases match tag %r, %r" % (
            len(releases), tag, releases))

    release = releases[0]
    return release['release_id'], release


def _tag2release_fedora(tag):
    """ Just guess which release correspond with this koji tag.

    For unknown reasons, the Fedora PDC instance doesn't have a
    koji_allowed_tags field associated with a release that we could use to
    determine this.  So, just guess for now until we resolve that.
    """
    if tag == rawhide_tag():
        release = {
            'name': 'Fedora',
            'short': 'fedora',
            'version': tag.strip('f'),
            'release_type': 'ga',
        }
        release_id = "{short}-{version}".format(**release)
    elif tag.endswith('-docker'):
        release = {
            'name': 'Fedora Updates',
            'short': 'fedora',
            'version': tag.strip('-docker').strip('f'),
            'release_type': 'updates',
        }
        release_id = "{short}-{version}-{release_type}".format(**release)
    elif tag.endswith('-container'):
        release = {
            'name': 'Fedora Updates',
            'short': 'fedora',
            'version': tag.strip('-container').strip('f'),
            'release_type': 'updates',
        }
        release_id = "{short}-{version}-{release_type}".format(**release)
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


def get_token(pdc_api_url, keytab):
    """
    Uses kerberos keytab for automatic authentication
    and retrieves the token from pdc-updater
    """
    if not os.path.exists(keytab):
        raise IOError("Keytab file not found")

    os.environ['KRB5_CLIENT_KTNAME'] = 'FILE:{0}'.format(keytab)
    headers = {'Accept': 'application/json'}

    try:
        auth = requests_kerberos.HTTPKerberosAuth()
        url = '{0}/auth/token/obtain/'.format(pdc_api_url.rstrip('/'))
        r = requests.get(url, headers=headers, auth=auth)
    except requests.exceptions.RequestException as error:
        log.exception('The following error occurred when trying to get a '
                      'token from PDC: {0}'.format(str(error)))
    return r.json()['token']
