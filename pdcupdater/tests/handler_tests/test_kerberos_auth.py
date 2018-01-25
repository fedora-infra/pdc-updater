import os

from mock import patch, Mock

import pdcupdater.utils


class TestKerberosAuthentication(object):
    @patch('os.path.exists', return_value=True)
    @patch('requests_kerberos.HTTPKerberosAuth')
    @patch('requests.get')
    def test_get_token(self, requests_get, kerb_auth, os_path):
        self.url = 'https://pdc.fedoraproject.org/rest_api/v1/'
        set_env = patch.dict(
            os.environ, {'KRB5_CLIENT_KTNAME': '/etc/foo.keytab'})
        requests_rv = Mock()
        requests_rv.json.return_value = {"token": "12345"}
        requests_get.return_value = requests_rv
        set_env.start()
        rv = pdcupdater.utils.get_token(self.url, '/etc/foo.keytab')
        set_env.stop()
        assert rv == '12345'
