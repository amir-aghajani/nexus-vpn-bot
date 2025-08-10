import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from utils import deep_json_load

urllib3.disable_warnings(InsecureRequestWarning)


class SanaeiXuiClient:
    def __init__(self, panel_url, username, password):
        self.base_url = panel_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        self.is_logged_in = False
        self.base_api_url = '/panel/api/inbounds'

    def _request(self, method, path, **kwargs):
        if not self.is_logged_in and path != '/login':
            if not self.login():
                return None

        url = self.base_url + path

        try:
            response = self.session.request(method, url, verify=False, timeout=20, **kwargs)

            if response.status_code in [401, 403]:
                if not self.login(): return None
                response = self.session.request(method, url, verify=False, timeout=20, **kwargs)

            if not response.ok:
                return None

            return deep_json_load(response.json())

        except Exception as e:
            return False

    def login(self):
        self.is_logged_in = False
        payload = {'username': self.username, 'password': self.password}
        response_data = self._request('post', '/login', data=payload)

        if response_data and response_data.get('success'):
            if self.session.cookies:
                self.is_logged_in = True
                return True
            else:
                return False
        else:
            return False

    def check_login(self):
        if self.is_logged_in:
            return True

        return self.login()

    def list_of_inbounds(self):
        if not self.check_login():
            return False

        response = self._request('get', f'{self.base_api_url}/list')

        if response and response.get('success'):
            return response.get('obj', [])
        else:
            return False

    def test_client_connection(self):
        if not self.login():
            return False

        return True
