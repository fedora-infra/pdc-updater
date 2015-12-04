import requests
import pdcupdater.handlers


class NewComposeHandler(pdcupdater.handlers.BaseHandler):
    """ When pungi-koji finishes a new compose. """

    def __init__(self, *args, **kwargs):
        super(NewComposeHandler, self).__init__(*args, **kwargs)
        self.old_composes_url = self.config['pdcupdater.old_composes_url']

    def can_handle(self, msg):
        return msg['topic'].endswith('pungi.compose.finish')

    def handle(self, pdc, msg):
        # This is something like Fedora-24-20151130.n.2
        compose_id = msg['msg']['compose_id']

        # TODO -- we're not actually sure what this is going to be called in
        # the message payload yet...
        release_id = msg['msg']['release_id']

        koji = "https://kojipkgs.fedoraproject.org"
        tmpl = "{koji}/compose/{release_id}/{compose_id}"
        compose_url = tmpl.format(
            koji=koji,
            release_id=release_id,
            compose_id=compose_id,
        )

        self._import_compose(pdc, release_id, compose_id, compose_url)

    def audit(self, pdc):
        raise NotImplementedError()

    def initialize(self, pdc):
        old_composes = pdcupdater.services.old_composes(self.old_composes_url)
        for release_id, compose_id, url in old_composes:
            self._import_compose(pdc, release_id, compose_id, url)

    def _import_compose(self, pdc, release_id, compose_id, compose_url):
        base = compose_url + "/compose/metadata"

        url = base + '/composeinfo.json'
        response = requests.get(url)
        if not bool(response):
            raise IOError("Failed to get %r: %r" % (url, response))
        composeinfo = response.json()

        url = base + '/images.json'
        response = requests.get(url)
        if not bool(response):
            raise IOError("Failed to get %r: %r" % (url, response))
        images = response.json()

        url = base + '/rpms.json'
        response = requests.get(url)
        if not bool(response):
            raise IOError("Failed to get %r: %r" % (url, response))
        rpms = response.json()

        # https://github.com/product-definition-center/product-definition-center/issues/228
        # https://pdc.fedorainfracloud.org/rest_api/v1/compose-images/
        pdc['compose-images']._(dict(
            release_id=release_id,
            composeinfo=composeinfo,
            image_manifest=images,
        ))
        # https://pdc.fedorainfracloud.org/rest_api/v1/compose-rpms/
        pdc['compose-rpms']._(dict(
            release_id=release_id,
            composeinfo=composeinfo,
            rpm_manifest=rpms,
        ))

