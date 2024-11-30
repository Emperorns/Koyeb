import requests

class KoyebClient:
    def __init__(self, api_key=None, email=None, password=None):
        self.api_key = api_key
        self.email = email
        self.password = password
        self.base_url = "https://api.koyeb.com/v1"

    def authenticate(self):
        if self.api_key:
            self.headers = {"Authorization": f"Bearer {self.api_key}"}
        elif self.email and self.password:
            auth_response = requests.post(
                f"{self.base_url}/auth/token",
                json={"email": self.email, "password": self.password},
            )
            self.headers = {"Authorization": f"Bearer {auth_response.json()['token']}"}
        else:
            raise ValueError("Either API key or email and password must be provided")

    def create_app(self, name, docker_image):
        self.authenticate()
        response = requests.post(
            f"{self.base_url}/apps",
            headers=self.headers,
            json={"name": name, "docker_image": docker_image},
        )
        return response.json()

    def deploy_app(self, app_id, docker_image):
        self.authenticate()
        response = requests.post(
            f"{self.base_url}/apps/{app_id}/deployments",
            headers=self.headers,
            json={"docker_image": docker_image},
        )
        return response.json()

    def delete_app(self, app_id):
        self.authenticate()
        response = requests.delete(
            f"{self.base_url}/apps/{app_id}", headers=self.headers
        )
        return response.json()

    def get_apps(self):
        self.authenticate()
        response = requests.get(f"{self.base_url}/apps", headers=self.headers)
        return response.json()
