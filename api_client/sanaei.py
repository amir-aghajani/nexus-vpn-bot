import json
import random
import string
import uuid
from datetime import datetime, timedelta, UTC

import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from utils import deep_json_load

urllib3.disable_warnings(InsecureRequestWarning)

AVAILABLE_INBOUND_PROTOCOLS = ['vless', 'vmess', 'trojan']


class SanaeiClient:
    def __init__(self, panel_url, username, password):
        self.base_url = panel_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        self.base_api_url = '/panel/api/inbounds'

        self.login()

    def _request(self, method, path, api: bool = True, **kwargs):
        if api:
            url = f'{self.base_url}{self.base_api_url}{path}'
        else:
            url = f'{self.base_url}{path}'

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

    def add_client(self, inbound_id, inbound_data) -> bool:
        try:
            self._request('post', f'/addClient', data={
                'id': inbound_id,
                'settings': json.dumps({
                    'clients': [inbound_data]
                })
            }, api=True)

            return True
        except Exception as e:
            print(e)

            return False

    def create_sub(self, duration, bandwidth, user_tg_id: int = None):
        created_clients = 0

        list_of_inbounds = self.list_of_inbounds()
        if len(list_of_inbounds) == 0:
            raise ValueError(f'NO INBOUNDS FOUND IN \'{self.base_url}\'')

        total_bandwidth = bandwidth * 1073741824
        expiry_date = datetime.now(UTC) + timedelta(days=duration)
        sub_id = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        sub_uuid = str(uuid.uuid4())
        sub_email = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        base_inbound = {
            'limitIp': 0,
            'totalGB': total_bandwidth,
            'expiryTime': int(expiry_date.timestamp()) * 1000,
            'enable': True,
            'tgId': user_tg_id,
            'subId': sub_id,
            'comment': 'AUTO_GENERATED_BY_NEXUS',
            'reset': 0
        }

        for inbound in list_of_inbounds:
            if inbound['protocol'] not in AVAILABLE_INBOUND_PROTOCOLS:
                continue

            inbound_data = {}

            if inbound['protocol'] == 'vless':
                inbound_data = {
                    'id': sub_uuid,
                    'flow': ''
                }
            elif inbound['protocol'] == 'vmess':
                inbound_data = {
                    'id': sub_uuid,
                    'security': 'auto'
                }
            elif inbound['protocol'] == 'trojan':
                inbound_data = {
                    'password': sub_uuid,
                }

            inbound_data.update({
                'email': sub_email + '_INBOUD_' + str(inbound['id']),
                **base_inbound
            })

            self.add_client(inbound_id=inbound['id'], inbound_data=inbound_data)
            created_clients += 1

        if created_clients == 0:
            raise ValueError(f'NO SUPPORTED INBOUNDS IN \'{self.base_url}\'')

        return {
            'subEmail': sub_email,
            'subUUID': sub_uuid,
            'subID': sub_id
        }

    def get_client_traffic(self, client_uuid):
        return self._request('get', f'/getClientTrafficsById/{client_uuid}', api=True)

    def get_sub_base_url(self):
        response = self._request('post', '/panel/setting/defaultSettings', api=False)

        sub_uri = response.get('subURI')
        if not sub_uri:
            raise ValueError('Subcription is not enabled on Sanaei panel')

        return sub_uri