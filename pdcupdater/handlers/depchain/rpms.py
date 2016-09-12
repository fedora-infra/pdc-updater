""" Handlers for an RPM dependency chain model.

The idea here is that these are two of what will eventually be many handlers
that build and maintain a dependency chain in PDC.

There are two handlers here.  They both respond to koji 'tag' events. One of
them figures out what the build required at *build* time, and updates PDC with
that. The other figures out what the build requires at *run* time, and updates
PDC with that.

"""

import logging
import time

import pdcupdater.handlers
import pdcupdater.services
from pdcupdater.utils import (
    tag2release,
    interesting_tags,
)


log = logging.getLogger(__name__)


class BaseRPMDepChainHandler(pdcupdater.handlers.BaseHandler):
    """ Abstract base class. """

    # A list of the types of relationships this thing manages.
    # This needs to be overridden by subclasses of this base class.
    managed_types = None

    def __init__(self, *args, **kwargs):
        super(BaseRPMDepChainHandler, self).__init__(*args, **kwargs)
        self.koji_url = self.config['pdcupdater.koji_url']

    @property
    def topic_suffixes(self):
        return ['buildsys.tag']

    def can_handle(self, msg):
        if not any([msg['topic'].endswith(suffix)
                    for suffix in self.topic_suffixes]):
            return False

        # Ignore secondary arches for now
        if msg['msg']['instance'] != 'primary':
            log.debug("From %r.  Skipping." % (msg['msg']['instance']))
            return False

        interesting = interesting_tags()
        tag = msg['msg']['tag']

        if tag not in interesting:
            log.debug("%r not in %r.  Skipping."  % (tag, interesting))
            return False

        return True

    def _yield_managed_pdc_relationships(self, pdc, release_id):
        for relationship_type in self.managed_types:
            entries = pdc.get_paged(
                pdc['release-component-relationships']._,
                from_component_release=release_id,
                type=relationship_type,
            )
            for entry in entries:
                # Filter out any irrelevant relationships (those of some type
                # managed by a different pdc updater Handler).
                relationship_type = entry['type']
                if relationship_type not in self.managed_types:
                    continue

                # Construct and yield a three-tuple result.
                keys = ('name', 'release')
                parent = dict(zip(keys, [entry['from_component'][key] for key in keys]))
                child = dict(zip(keys, [entry['to_component'][key] for key in keys]))
                yield parent, relationship_type, child

    def _yield_koji_relationships(self, pdc, tag):

        release_id, release = tag2release(tag)
        # TODO -- this tag <-> release agreement is going to break down with modularity.

        pdcupdater.utils.ensure_release_exists(pdc, release_id, release)

        builds = pdcupdater.services.koji_builds_in_tag(self.koji_url, tag)

        for build in builds:
            parent = {'name': build['name'], 'release': release_id}

            relationships = self.get_koji_relationships_from_build(
                self.koji_url, build['build_id'])
            relationships = list(relationships)

            for relationship_type, child_name in relationships:
                child = {'name': child_name, 'release': release_id}
                yield parent, relationship_type, child

    def handle(self, pdc, msg):
        tag = msg['msg']['tag']
        release_id, release = tag2release(tag)

        # TODO -- this tag <-> release agreement is going to break down with modularity.
        pdcupdater.utils.ensure_release_exists(pdc, release_id, release)

        name = msg['msg']['name']
        build_id = msg['msg']['build_id']
        parent = pdcupdater.utils.ensure_release_component_exists(
            pdc, release_id, name)

        # Go to sleep due to a race condition that is koji's fault.
        # It publishes a fedmsg message before the task is actually done and
        # committed to their database.  In the next step, we try to query
        # them -- but if the task isn't done, we get an exception.
        time.sleep(1)

        # First, go through all of the relationships that we learn from koji,
        # and add them to PDC.  Some may already be present, but we may add new
        # ones here.
        log.info("Gathering relationships from koji for %r" % build_id)
        koji_relationships = list(self.get_koji_relationships_from_build(
            self.koji_url, build_id))
        log.info("Ensuring PDC relations are in place for %r" % build_id)
        for relationship_type, child_name in koji_relationships:
            child = pdcupdater.utils.ensure_release_component_exists(
                pdc, release_id, child_name)
            pdcupdater.utils.ensure_release_component_relationship_exists(
                pdc, parent=parent, child=child, type=relationship_type)

        # Lastly, go through all of the relationships that we know of now in
        # PDC and find any that do not appear in koji.  These must be old
        # relationships that are no longer relevant.
        # In order to do that, first build two easily comparable lists.

        log.info("Pruning dropped relationships for %r" % build_id)
        # Here's the first.  We re-format the koji_relationships list.
        koji_relationships = [
            (
                dict(name=name, release=release_id),
                relationship_type,
                dict(name=child_name, release=release_id)
            ) for relationship_type, child_name in koji_relationships]

        # Here's the second.  Build and similarly format a PDC list.
        pdc_relationships = list(self._yield_managed_pdc_relationships(pdc, release_id))

        # Now that we have those two equivalently-formatted lists, step through
        # the list in PDC, and delete any entries that do not also appear in
        # the koji list.
        for pdc_parent, pdc_type, pdc_child in pdc_relationships:
            if (pdc_parent, pdc_type, pdc_child) not in koji_relationships:
                pdcupdater.utils.delete_release_component_relationship(
                    pdc, parent=pdc_parent, child=pdc_child, type=pdc_type)

    def audit(self, pdc):
        present, absent = set(), set()
        tags = interesting_tags()

        for tag in tags:
            log.debug("Starting audit of tag %r." % tag)
            release_id, release = tag2release(tag)

            # Query Koji and PDC to figure out their respective opinions
            koji_relationships = list(self._yield_koji_relationships(pdc, tag))
            pdc_relationships = list(self._yield_managed_pdc_relationships(pdc, release_id))

            # normalize the two lists, and smash items into hashable strings.
            def _format(parent, relationship_type, child):
                return "%s/%s %s %s/%s" % (
                    parent['name'], parent['release'],
                    relationship_type,
                    child['name'], child['release'],
                )
            koji_relationships = set([_format(*x) for x in koji_relationships])
            pdc_relationships = set([_format(*x) for x in pdc_relationships])

            # use set operators to determine the difference
            present = present.union(pdc_relationships - koji_relationships)
            absent = absent.union(koji_relationships - pdc_relationships)

        return present, absent

    def initialize(self, pdc):
        tags = interesting_tags()

        for tag in tags:
            log.debug("Starting initialize of tag %r." % tag)
            release_id, release = tag2release(tag)
            pdcupdater.utils.ensure_release_exists(pdc, release_id, release)

            koji_relationships = self._yield_koji_relationships(pdc, tag)
            for parent, relationship_type, child in koji_relationships:
                parent = pdcupdater.utils.ensure_release_component_exists(
                    pdc, parent['release'], parent['name'])
                child = pdcupdater.utils.ensure_release_component_exists(
                    pdc, child['release'], child['name'])
                pdcupdater.utils.ensure_release_component_relationship_exists(
                    pdc, parent=parent, child=child, type=relationship_type)



class NewRPMBuildTimeDepChainHandler(BaseRPMDepChainHandler):
    """ When a build gets tagged, update PDC with buildroot info. """

    # A list of the types of relationships this thing manages.
    managed_types = ('RPMBuildRequires', 'RPMBuildRoot')

    def get_koji_relationships_from_build(self, koji_url, build_id):

        # Get all RPMs for a build..
        build, rpms = pdcupdater.services.koji_rpms_from_build(
            koji_url, build_id)

        # https://pdc.fedoraproject.org/rest_api/v1/rpms/
        for filename in rpms:
            # Look up the *build time* deps
            buildroot = pdcupdater.services.koji_list_buildroot_for(
                self.koji_url, filename)
            for entry in buildroot:
                child_name = entry['name']
                if entry['is_update']:
                    relationship_type = 'RPMBuildRequires'
                else:
                    relationship_type = 'RPMBuildRoot'
                yield relationship_type, child_name


class NewRPMRunTimeDepChainHandler(BaseRPMDepChainHandler):
    """ When a build gets tagged, update PDC with rpm dep info. """

    # A list of the types of relationships this thing manages.
    managed_types = ('RPMRequires',)

    def get_koji_relationships_from_build(self, koji_url, build_id):

        # Get all RPMs for a build..
        build, rpms = pdcupdater.services.koji_rpms_from_build(
            koji_url, build_id)

        for filename in rpms:
            # Look up the *install time* deps
            requirements = pdcupdater.services.koji_yield_rpm_requires(
                self.koji_url, filename)
            for name, qualifier, version in requirements:
                # XXX - we're dropping any >= or <= information here, which is
                # OK for now.  All we need to know is that there is a
                # dependency.
                yield 'RPMRequires', name
