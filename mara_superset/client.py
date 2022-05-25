import requests
import json
from urllib.parse import urljoin

from . import config

class SupersetClient(object):
    """
    A client class for interacting with the Superset API
    
    See also: https://superset.apache.org/docs/api
    """
    def __init__(self):
        self.base_url = urljoin(config.internal_superset_url(),'/api/v1')
        self.token = None
        self.refresh_token = None
        self.session = requests.Session()

        response = self.session.post(
            self.base_url + '/security/login',
            json={'username': config.superset_api_username(),
                  'password': config.superset_api_password(),
                  'provider': 'db',
                  'refresh': True})

        response.raise_for_status()

        tokens = response.json()
        self.token = tokens.get('access_token')
        self.refresh_token = tokens.get('refresh_token')

        # Get CSFR Token
        self.csrf_token = None
        response = self.session.get(
            self.base_url + '/security/csrf_token',
            headers=self._headers
        )
        response.raise_for_status() # Check CSRF Token went well
        self.csrf_token = response.json().get("result")

    def request(self, method, path, data = None):
        print(f'{method.__name__} {self.base_url + path} {json.dumps(data) if data else ""}')
        response = method(self.base_url + path, headers=self._headers, json=data)
        if response.status_code < 200 or response.status_code >= 300:
            raise Exception(f'{response.status_code}: {response.text}')
        elif response.text:
            return response.json()
        else:
            return None

    @property
    def _headers(self):
        return {
            "Authorization": f'Bearer {self.token}',
            "X-CSRFToken": f'{self.csrf_token}'
        }

    def get(self, path) -> dict:
        return self.request(self.session.get, path)

    def post(self, path, data=None) -> dict:
        return self.request(self.session.post, path, data)

    def put(self, path, data=None) -> dict:
        return self.request(self.session.put, path, data)

    def delete(self, path, data=None) -> dict:
        return self.request(self.session.delete, path, data)