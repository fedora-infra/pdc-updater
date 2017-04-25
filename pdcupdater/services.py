import logging
import operator

import bs4
import requests

import pdcupdater.handlers.compose
import pdcupdater.utils

log = logging.getLogger(__name__)

import dogpile.cache
cache = dogpile.cache.make_region()
cache.configure('dogpile.cache.memory', expiration_time=300)


def _scrape_links(session, url):
    """ Utility to scrape links from a <pre> tag. """
    log.debug('Scraping %s', url)
    response = session.get(url)
    if not bool(response):
        raise IOError("Couldn't talk to %r, %r" % (url, response))
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    pre = soup.find('pre')
    for link in pre.findAll('a'):
        href = link.attrs.get('href', '').strip('/')
        if not href:
            continue
        if href.startswith('?'):
            continue
        href = url.strip('/') + '/' + href.strip('/')
        yield link.text.strip('/'), href


def old_composes(base_url):
    """ Screen-scrape the list of old composes from kojipkgs. """

    session = requests.Session()

    # Get the initial list of branches
    branch_links = _scrape_links(session, base_url)
    for branch, branch_link in branch_links:
        # Find all composes for that branch
        compose_links = _scrape_links(session, branch_link)
        for compose, compose_link in compose_links:
            # Some of these are symlinks to others
            if compose.startswith('latest'):
                log.debug("Skipping %s.  Just a symlink." % compose_link)
                continue

            # Some of these failed mid-way and didn't complete.
            metadata_link = compose_link + '/compose/metadata/'
            filenames = ['composeinfo', 'images', 'rpms']
            urls = [metadata_link + fname + '.json' for fname in filenames]
            good = all([bool(session.head(url)) for url in urls])
            if not good:
                continue

            # But really, the real check is to see if the status is good.
            response = session.get(compose_link + '/STATUS')
            if not bool(response):
                continue
            if not response.text.strip() in pdcupdater.handlers.compose.final:
                continue

            # If we got this far, then return it
            log.info("  found %s/%s" % (branch, compose))
            yield branch, compose, compose_link

    # Finally, close the requests session.
    session.close()


@pdcupdater.utils.with_ridiculous_timeout
def fas_persons(base_url, username, password):
    """ Return the list of users in the Fedora Account System. """

    import fedora.client
    import fedora.client.fas2

    log.info("Connecting to FAS at %r" % base_url)
    fasclient = fedora.client.fas2.AccountSystem(
        base_url=base_url, username=username, password=password)

    log.info("Downloading FAS userlist...")
    response = fasclient.send_request(
        '/user/list', req_params={'search': '*'}, auth=True, timeout=600)

    return response['people']


@pdcupdater.utils.retry()
def koji_list_buildroot_for(url, filename, tries=3):
    """ Return the list of koji builds in the buildroot of a built rpm. """

    import koji
    session = koji.ClientSession(url)
    rpminfo = session.getRPM(filename)
    if type(rpminfo) == list:
        if not tries:
            raise TypeError("Got a list back from koji.getRPM(%r)" % filename)
        # Try again.. this is weird behavior...
        return koji_list_buildroot_for(url, filename, tries-1)
    return session.listRPMs(componentBuildrootID=rpminfo['buildroot_id'])


@pdcupdater.utils.retry()
def koji_yield_rpm_requires(url, nvra):
    """ Yield three-tuples of RPM requirements from a koji nvra.

    Inspired by koschei/backend/koji_util.py by mizdebsk.
    """
    import koji
    import rpm
    session = koji.ClientSession(url)

    # Set up some useful structures before we get started.
    header_lookup = {
        rpm.RPMSENSE_LESS: '<',
        rpm.RPMSENSE_GREATER: '>',
        rpm.RPMSENSE_EQUAL: '=',
    }
    relevant_flags = reduce(operator.ior, header_lookup.keys())

    # Query koji and step over all the deps listed in the raw rpm headers.
    deps = session.getRPMDeps(nvra, koji.DEP_REQUIRE)
    for dep in deps:
        flags = dep['flags']

        # The rpmlib headers here contain some crazy dep flags that aren't
        # relevant to normal humans.  Internal rpmlib dep information.
        if flags & ~(relevant_flags):
            continue

        # Bit-shift our way through the flags to figure out how this
        # relationship is qualified.
        qualifier = ""
        while flags:
            old = flags
            flags &= flags - 1
            qualifier += header_lookup[old ^ flags]

        # Yield back ('foo', '<=', '1.0.1')
        yield dep['name'], qualifier, dep['version'].rstrip()


#@pdcupdater.utils.retry()
def koji_builds_in_tag(url, tag, owner=None):
    """ Return the list of koji builds in a tag. """
    import koji
    log.info("Listing rpms in koji(%s) tag %s" % (url, tag))
    session = koji.ClientSession(url)
    try:
        return session.listTagged(tag, latest=True, owner=owner)
    except koji.GenericError as e:
        log.warn("Failed to get builds in tag %r: %r" % (tag, e))
        return []


@pdcupdater.utils.retry()
def koji_rpms_in_tag(url, tag):
    """ Return the list of koji rpms in a tag. """
    import koji
    log.info("Listing rpms in koji(%s) tag %s" % (url, tag))
    session = koji.ClientSession(url)

    try:
        rpms, builds = session.listTaggedRPMS(tag, latest=True)
    except koji.GenericError as e:
        log.exception("Failed to list rpms in tag %r" % tag)
        # If the tag doesn't exist.. then there are no rpms in that tag.
        return []

    # Extract some srpm-level info from the build attach it to each rpm
    builds = {build['build_id']: build for build in builds}
    for rpm in rpms:
        idx = rpm['build_id']
        rpm['srpm_name'] = builds[idx]['name']
        rpm['srpm_nevra'] = builds[idx]['nvr']

    return rpms


@cache.cache_on_arguments()
def koji_get_build(url, build_id):
    import koji
    session = koji.ClientSession(url)
    build = session.getBuild(build_id)
    if build:
        assert build['id'] == build_id, "%r != %r" % (build['id'], build_id)
    return build


@cache.cache_on_arguments()
def koji_archives_from_build(url, build_id):
    import koji
    session = koji.ClientSession(url)
    return session.listArchives(build_id)


@cache.cache_on_arguments()
def koji_rpms_from_archive(url, artifact):
    import koji
    session = koji.ClientSession(url)
    return session.listRPMs(imageID=artifact.get('id'))


@cache.cache_on_arguments()
@pdcupdater.utils.retry()
def koji_rpms_from_build(url, build_id):
    import koji
    log.info("Listing rpms in koji(%s) for %r" % (url, build_id))
    session = koji.ClientSession(url)
    build = koji_get_build(url, build_id)

    rpms = set()
    for rpm in session.listRPMs(buildID=build_id):
        rpms.add('{0}.{1}.rpm'.format(rpm['nvr'], rpm['arch']))

    # Dependable order for testing.
    rpms = list(sorted(rpms))
    return build, rpms


def pkgdb_packages(base_url, extra=False):
    """ Return a generator over all the packages in pkgdb.  """
    import pkgdb2client
    log.info("Connecting to pkgdb at %r" % base_url)
    pkgdb = pkgdb2client.PkgDB(url=base_url)
    result = pkgdb.get_packages(page='all')
    packages = result['packages']
    if extra:
        for i in range(len(packages)):
            package = pkgdb.get_package(packages[i]['name'])
            collections = [p['collection'] for p in package['packages']]
            packages[i]['collections'] = collections
            yield packages[i]
    else:
        for i in range(len(packages)):
            yield packages[i]



if __name__ == '__main__':

    # A little test by hand...
    logging.basicConfig(level=logging.DEBUG)
    composes = old_composes('https://kojipkgs.fedoraproject.org/compose/')
    composes = list(composes)
    for compose in composes:
        print compose
