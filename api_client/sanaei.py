import json

import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from utils import deep_json_load

urllib3.disable_warnings(InsecureRequestWarning)


class SanaeiClient:
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

        if path == '/login':
            url = f"{self.base_url}{path}"
        else:
            url = f"{self.base_url}{self.base_api_url}{path}"

        try:

            response = self.session.request(method, url, verify=False, timeout=20, **kwargs)
            if response.status_code in [401, 403]:
                if not self.login(): return None
                response = self.session.request(method, url, verify=False, timeout=20, **kwargs)

            if response.ok:
                return deep_json_load(response.json())

            return None

        except Exception as e:
            pass

    def login(self):
        self.is_logged_in = False
        payload = {'username': self.username, 'password': self.password}
        response_data = self._request('post', '/login', data=payload)
        self.is_logged_in = bool(response_data and response_data.get("success") and self.session.cookies)
        return self.is_logged_in

    def check_login(self):
        if self.is_logged_in:
            return True

        return self.login()

    def list_of_inbounds(self):
        response = self._request('get', '/list')
        if response and response.get('success'):
            return response.get('obj', [])
        else:
            return False

    def test_client_connection(self):
        if not self.login():
            return False

        return True

    def create_inbound(self, inbound_id, inbound_data):
        self._request('post', f'/addClient', data={
            'id': inbound_id,
            'settings': json.dumps({
                'clients': [inbound_data]
            })
        })

        return

    def get_client_traffic(self, client_uuid):
        response = self._request('get', f'/getClientTrafficsById/{client_uuid}')
        return response.get('obj') if response and response.get('success') else None
