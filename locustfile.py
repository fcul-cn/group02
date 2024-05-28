from locust import HttpUser, task, between

class HelloWorldUser(HttpUser):

    wait_time = between(1, 5)

    @task
    def hello_world(self):
        self.client.get("https://34.32.245.13/api/tracks/1")
        self.client.get("https://34.32.245.13/api/genres/1")
        self.client.get("https://34.32.245.13/api/artists/1")
        self.client.get("https://34.32.245.13/api/releases/1")
        self.client.get("https://34.32.245.13/api/playlists/1")

    def on_start(self):
        self.client.verify = False
