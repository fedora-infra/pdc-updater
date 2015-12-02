import logging
import socket

import fedora.client
import fedora.client.fas2

log = logging.getLogger(__name__)


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
    session = koji.ClientSession(url)
    rpms, builds = session.listTaggedRPMS(tag)
    return rpms
