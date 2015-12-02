import requests
import pdcupdater.handlers


class NewComposeHandler(pdcupdater.handlers.BaseHandler):
    """ When pungi-koji finishes a new compose. """

    def can_handle(self, msg):
        return msg['topic'].endswith('pungi.compose.finish')

    def handle(self, pdc, msg):
        idx = msg['msg']['compose_id']

        # TODO -- don't hardcode these two values.
        # get them from the pungi fedmsg message once we have an example.
        branch = 'rawhide'  # in kojipkgs terms
        prefix = 'Fedora-24'  # in kojipkgs terms
        release_id = 'rawhide'  # in PDC terms

        koji = "https://kojipkgs.fedoraproject.org"
        tmpl = "{koji}/compose/{branch}/{prefix}-{idx}/compose/metadata"
        base = tmpl.format(koji=koji, branch=branch, prefix=prefix, idx=idx)

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

    def audit(self, pdc):
        raise NotImplementedError()

    def initialize(self, pdc):
        raise NotImplementedError()
