import logging
import socket

import bs4
import requests

import fedora.client
import fedora.client.fas2
import pkgdb2client

log = logging.getLogger(__name__)


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
            yield branch, compose, compose_link

    # Finally, close the requests session.
    session.close()


def fas_persons(base_url, username, password):
    """ Return the list of users in the Fedora Account System. """

    fasclient = fedora.client.fas2.AccountSystem(
        base_url=base_url, username=username, password=password)

    timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(600)
    try:
        log.info("Downloading FAS userlist...")
        response = fasclient.send_request(
            '/user/list', req_params={'search': '*'}, auth=True)
    finally:
        socket.setdefaulttimeout(timeout)

    return response['people']


def koji_builds_in_tag(url, tag):
    import koji
    session = koji.ClientSession(url)
    rpms, builds = session.listTaggedRPMS(tag)
    return rpms


def pkgdb(base_url, acls=False):
    pkgdb = pkgdb2client.PkgDB(url=base_url)
    pkg = pkgdb.get_packages(page='all', acls=True)
    return pkg['packages']


if __name__ == '__main__':

    # A little test by hand...
    logging.basicConfig(level=logging.DEBUG)
    composes = old_composes('https://kojipkgs.fedoraproject.org/compose/')
    composes = list(composes)
    for compose in composes:
        print compose
