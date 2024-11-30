import requests

class KoyebAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = 'https://api.koyeb.com/v1'

    def login(self, api_key):
        self.api_key = api_key
        response = requests.post(f'{self.base_url}/auth/token', headers={'Content-Type': 'application/json'}, json={'api_key': api_key})
        if response.status_code == 200:
            self.token = response.json()['token']
        else:
            raise Exception('Invalid API key')

    def logout(self):
        self.api_key = None
        self.token = None

    def create_app(self, app_name):
        response = requests.post(f'{self.base_url}/apps', headers={'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}, json={'name': app_name})
        if response.status_code == 201:
            return response.json()['id']
        else:
            raise Exception('Failed to create app')

    def redeploy(self, app_id):
        response = requests.post(f'{self.base_url}/apps/{app_id}/redeploy', headers={'Authorization': f'Bearer {self.token}'})
        if response.status_code == 200:
            return 'App redeployed successfully'
        else:
            raise Exception('Failed to redeploy app')

    def get_logs(self, app_id):
        response = requests.get(f'{self.base_url}/apps/{app_id}/logs', headers={'Authorization': f'Bearer {self.token}'})
        if response.status_code == 200:
            return response.text
        else:
            raise Exception('Failed to get logs')

    def get_env_vars(self, app_id):
        response = requests.get(f'{self.base_url}/apps/{app_id}/env-vars', headers={'Authorization': f'Bearer {self.token}'})
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to get env vars')
