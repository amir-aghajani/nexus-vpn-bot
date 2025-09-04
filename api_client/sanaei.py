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
        self.base_api_url = '/panel/web/inbounds'

        self.login()

    def _request(self, method, path, api: bool = True, **kwargs):
        if api:
            url = f"{self.base_url}{self.base_api_url}{path}"
        else:
            url = f"{self.base_url}{path}"

        try:
            response = self.session.request(method, url, verify=False, timeout=20, **kwargs)

            if response.status_code in [401, 403]:
                self.login()
                response = self.session.request(method, url, verify=False, timeout=20, **kwargs)

            if not response.text:
                raise ValueError(
                    'Empty response from sever\n\n' +
                    'Requested URL:\n\n' + url
                )

            response_json = deep_json_load(response.json())
            return response_json.get('obj') or response_json
        except Exception as e:
            raise ValueError(f'Error during request to Sanaei panel: {str(e)}')

    def login(self):
        payload = {'username': self.username, 'password': self.password}
        response = self._request('post', '/login', api=False, data=payload)

        if not bool(response and self.session.cookies):
            raise ValueError(
                'Login to Sanaei panel failed. Please check server credentials!\n\n' +
                'Sever panel url:\n\n' + self.base_url
            )

    def list_of_inbounds(self):
        return self._request('get', '/list', api=True)

    def test_client_connection(self):
        self.login()
        return True

    def create_inbound(self, inbound_id, inbound_data):
        return self._request('post', f'/addClient', data={
            'id': inbound_id,
            'settings': json.dumps({
                'clients': [inbound_data]
            })
        }, api=True)

    def get_client_traffic(self, client_uuid):
        return self._request('get', f'/getClientTrafficsById/{client_uuid}', api=True)

    def get_sub_base_url(self):
        response = self._request('post', '/panel/setting/defaultSettings', api=False)

        sub_uri = response.get('subURI')
        if not sub_uri:
            raise ValueError('Subcription is not enabled on Sanaei panel')

        return sub_uri
