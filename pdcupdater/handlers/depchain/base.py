import collections
import logging
import time

import pdcupdater.handlers
import pdcupdater.services
import pdcupdater.utils


log = logging.getLogger(__name__)


class BaseKojiDepChainHandler(pdcupdater.handlers.BaseHandler):
    """ Abstract base class. """

    # A list of the types of relationships this thing manages.
    # This needs to be overridden by subclasses of this base class.
    managed_types = None
    # The types of the parents and children in our managed relationships
    parent_type = None
    child_type = None

    def construct_topics(self, config):
        # Return a single hardcoded topic when using STOMP
        if config.get('stomp_uri'):
            if config.get('zmq_enabled', False):
                raise Exception('pdc-updater cannot support both STOMP and ZMQ being enabled')
            else:
                return ['{0}.brew.build.tag'.format(config['topic_prefix'])]
        else:
            return [
                '.'.join([config['topic_prefix'], config['environment'], topic])
                for topic in self.topic_suffixes
            ]

    def _yield_koji_relationships_from_build(self, koji_url, build_id, rpms=None):
        raise NotImplementedError("Subclasses must implement this.")

    def _yield_koji_relationships_from_tag(self, koji_url, tag):
        raise NotImplementedError("Subclasses must implement this.")

    def interesting_tags(self, pdc):
        raise NotImplementedError("Subclasses must implement this.")

    def __init__(self, *args, **kwargs):

        # First, a sanity check...
        required = ('managed_types', 'parent_type', 'child_type',)
        for attr in required:
            if not getattr(self, attr, None):
                raise AttributeError("%r is required on %r" % (attr, self))

        super(BaseKojiDepChainHandler, self).__init__(*args, **kwargs)
        self.koji_url = self.config['pdcupdater.koji_url']
        self.io_threads = self.config.get('pdcupdater.koji_io_threads', 8)
        self.pdc_tag_mapping = self.config.get('pdcupdater.pdc_tag_mapping', False)

    @property
    def topic_suffixes(self):
        return [
            # Fedora messaging
            'buildsys.tag',
            # Red Hat.
            'brew.build.tag',
        ]

    @classmethod
    def extract_tag(cls, msg):
        if msg.get('headers'):
            return msg['headers']['tag']
        else:
            return msg['msg']['tag']

    @classmethod
    def extract_build_id(cls, msg):
        if 'build_id' in msg.get('msg', {}):
            return msg['msg']['build_id']
        else:
            return msg['msg']['build']['build_id']

    def can_handle(self, pdc, msg):
        if not any([msg['topic'].endswith(suffix)
                    for suffix in self.topic_suffixes]):
            return False

        # Ignore secondary arches for now
        instance = msg.get('msg', {}).get('instance', 'primary')
        if instance != 'primary':
            log.debug("From %r.  Skipping." % instance)
            return False

        interesting = self.interesting_tags(pdc)
        tag = self.extract_tag(msg)

        if tag not in interesting:
            log.debug("%r not in %r.  Skipping."  % (tag, interesting))
            return False

        return True

    def _yield_managed_pdc_relationships_from_release(self, pdc, release_id):
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

    def handle(self, pdc, msg):
        tag = self.extract_tag(msg)
        if self.pdc_tag_mapping:
            release_id, release = pdcupdater.utils.tag2release(tag, pdc=pdc)
        else:
            release_id, release = pdcupdater.utils.tag2release(tag)

        # TODO -- this tag <-> release agreement is going to break down with modularity.
        pdcupdater.utils.ensure_release_exists(pdc, release_id, release)

        build_id = self.extract_build_id(msg)

        # Go to sleep due to a race condition that is koji's fault.
        # It publishes a fedmsg message before the task is actually done and
        # committed to their database.  In the next step, we try to query
        # them -- but if the task isn't done, we get an exception.
        #
        # Here's the koji branch that has some code which will ultimately let
        # us get rid of this sleep statement:
        # https://github.com/mikem23/koji-playground/commits/post-commit-callback
        time.sleep(1)

        # We're going to do things in terms of bulk operations, so first find
        # all the relationships from koji, then find all the relationships from
        # pdc.  We'll study the intersection between the two sets and act on
        # the discrepancies.
        log.info("Gathering relationships from koji for %r" % build_id)
        koji_relationships = set(self._yield_koji_relationships_from_build(
            self.koji_url, build_id))

        # Consolidate those by the parent/from_component
        by_parent = collections.defaultdict(set)
        for parent_name, relationship, child_name in koji_relationships:
            by_parent[parent_name].add((relationship, child_name,))

        # Finally, iterate over all those, now grouped by parent_name
        for parent_name, koji_relationships in by_parent.items():
            # TODO -- pass in global_component_name to this function?
            parent = pdcupdater.utils.ensure_release_component_exists(
                pdc, release_id, parent_name, type=self.parent_type)

            log.info("Gathering from pdc for %s/%s" % (parent_name, release_id))
            pdc_relationships = set(self._yield_pdc_relationships_from_build(
                pdc, parent['name'], release_id))

            to_be_created = koji_relationships - pdc_relationships
            to_be_deleted = pdc_relationships - koji_relationships

            log.info("Issuing bulk create for %i entries" % len(to_be_created))
            pdcupdater.utils.ensure_bulk_release_component_relationships_exists(
                pdc, parent, to_be_created, component_type=self.child_type)

            log.info("Issuing bulk delete for %i entries" % len(to_be_deleted))
            pdcupdater.utils.delete_bulk_release_component_relationships(
                pdc, parent, to_be_deleted)

    def audit(self, pdc):
        present, absent = set(), set()
        tags = self.interesting_tags(pdc)

        for tag in tags:
            log.info("Starting audit of tag %r of %r." % (tag, tags))
            if self.pdc_tag_mapping:
                release_id, release = pdcupdater.utils.tag2release(tag, pdc=pdc)
            else:
                release_id, release = pdcupdater.utils.tag2release(tag)

            # Query Koji and PDC to figure out their respective opinions
            koji_relationships = list(self._yield_koji_relationships_from_tag(pdc, tag))
            pdc_relationships = list(self._yield_managed_pdc_relationships_from_release(pdc, release_id))

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
        tags = self.interesting_tags(pdc)
        tags.reverse()

        for tag in tags:
            log.info("Starting initialize of tag %r of %r." % (tag, tags))
            if self.pdc_tag_mapping:
                release_id, release = pdcupdater.utils.tag2release(tag, pdc=pdc)
            else:
                release_id, release = pdcupdater.utils.tag2release(tag)
            pdcupdater.utils.ensure_release_exists(pdc, release_id, release)

            # Figure out everything that koji knows about this tag.
            koji_relationships = self._yield_koji_relationships_from_tag(pdc, tag)

            # Consolidate those by the parent/from_component
            children = []
            old_parent = None
            for parent, relationship, child in koji_relationships:
                # This only gets triggered the first time through the loop.
                if not old_parent:
                    old_parent = parent

                # If switching to a new parent key, then issue bulk create
                # statements for each parent
                if parent != old_parent:
                    pdcupdater.utils.ensure_release_component_exists(
                        pdc, release_id, parent['name'], type=self.parent_type)
                    pdcupdater.utils.ensure_bulk_release_component_relationships_exists(
                        pdc, parent, children, component_type='rpm')
                    # Reset things...
                    children = []
                    old_parent = parent

                children.append((relationship, child['name'],))

    def _yield_pdc_relationships_from_build(self, pdc, name, release):
        for relationship_type in self.managed_types:
            entries = pdc.get_paged(
                pdc['release-component-relationships']._,
                from_component_name=name,
                from_component_release=release,
                type=relationship_type,
            )
            for entry in entries:
                # Filter out unmanaged types (just to be sure..)
                if entry['type'] not in self.managed_types:
                    continue
                yield entry['type'], entry['to_component']['name']
