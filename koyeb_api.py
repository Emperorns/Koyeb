import requests

class KoyebAPI:
    def __init__(self):
        self.base_url = 'https://api.koyeb.com/v1'
        self.access_token = None

    def login(self, api_key):
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.get(f'{self.base_url}/auth', headers=headers)
        if response.status_code == 200:
            self.access_token = response.json()['access_token']
        else:
            raise Exception(f'Login failed: {response.text}')

    def logout(self):
        self.access_token = None

    def create_app(self, app_name):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.post(f'{self.base_url}/apps', headers=headers, json={'name': app_name})
        if response.status_code != 201:
            raise Exception(f'App creation failed: {response.text}')

    def deploy(self, app_id):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.post(f'{self.base_url}/apps/{app_id}/deploy', headers=headers)
        if response.status_code != 202:
            raise Exception(f'Deployment failed: {response.text}')

    def redeploy(self, app_id):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.post(f'{self.base_url}/apps/{app_id}/redeploy', headers=headers)
        if response.status_code != 202:
            raise Exception(f'Redeployment failed: {response.text}')

    def get_logs(self, app_id):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f'{self.base_url}/apps/{app_id}/logs', headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f'Log retrieval failed: {response.text}')

    def get_env_vars(self, app_id):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f'{self.base_url}/apps/{app_id}/env-vars', headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f'Env var retrieval failed: {response.text}')

    def set_env_var(self, app_id, key, value):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.post(f'{self.base_url}/apps/{app_id}/env-vars', headers=headers, json={'key': key, 'value': value})
        if response.status_code != 201:
            raise Exception(f'Env var setting failed: {response.text}')

    def get_env_var(self, app_id, key):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f'{self.base_url}/apps/{app_id}/env-vars/{key}', headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f'Env var retrieval failed: {response.text}')

    def delete_env_var(self, app_id, key):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.delete(f'{self.base_url}/apps/{app_id}/env-vars/{key}', headers=headers)
        if response.status_code != 204:
            raise Exception(f'Env var deletion failed: {response.text}')

    def list_apps(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f'{self.base_url}/apps', headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f'App listing failed: {response.text}')

    def get_app(self, app_id):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f'{self.base_url}/apps/{app_id}', headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f'App retrieval failed: {response.text}')

    def delete_app(self, app_id):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.delete(f'{self.base_url}/apps/{app_id}', headers=headers)
        if response.status_code != 204:
            raise Exception(f'App deletion failed: {response.text}')
