import functools
import logging
import socket

import bs4
import requests

log = logging.getLogger(__name__)

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

            # If we got this far, then return it
            log.info("  found %s/%s" % (branch, compose))
            yield branch, compose, compose_link

    # Finally, close the requests session.
    session.close()


@with_ridiculous_timeout
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


def koji_builds_in_tag(url, tag):
    """ Return the list of koji builds in a tag. """
    import koji
    log.info("Listing rpms in koji(%s) tag %s" % (url, tag))
    session = koji.ClientSession(url)
    rpms, builds = session.listTaggedRPMS(tag)

    # Extract some srpm-level info from the build attach it to each rpm
    builds = {build['build_id']: build for build in builds}
    for rpm in rpms:
        idx = rpm['build_id']
        rpm['srpm_name'] = builds[idx]['name']
        rpm['srpm_nevra'] = builds[idx]['nvr']

    return rpms


def koji_rpms_from_build(url, build_id):
    import koji
    log.info("Listing rpms in koji(%s) for %r" % (url, build_id))
    session = koji.ClientSession(url)
    build = session.getBuild(build_id)
    children = session.getTaskChildren(build['task_id'])

    rpms = set()
    for child in children:
        results = session.getTaskResult(child['id'])
        if not results:
            continue

        # rpm looks like 'tasks/4547/12094547/podofo-0.9.1-17.el7.ppc64.rpm'
        for rpm in results.get('rpms', []):
            rpms.add(rpm.split('/')[-1])
        for rpm in results.get('srpms', []):
            rpms.add(rpm.split('/')[-1])

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
