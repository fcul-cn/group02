from locust import HttpUser, task, between

class HelloWorldUser(HttpUser):

    wait_time = between(3.0, 10.5)

    @task
    def hello_world(self):
        self.client.get("https://34.90.127.247/api/tracks/1")
        self.client.get("https://34.90.127.247/api/genres/1")
        self.client.get("https://34.90.127.247/api/artists/1")
        self.client.get("https://34.90.127.247/api/releases/1")
        self.client.get("https://34.90.127.247/api/playlists/1")

    def on_start(self):
        self.bearer_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImRzeVNJcVg2MEliY0tWSUVQel9qbiJ9.eyJpc3MiOiJodHRwczovL2Rldi1hanYyeTUyemhldXkyZGpvLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDEwNDkwMzQwMzMxMzA0NDkxMzMxNiIsImF1ZCI6WyJodHRwczovLzM0LjkwLjE2Ni4xNzUvYXBpIiwiaHR0cHM6Ly9kZXYtYWp2Mnk1MnpoZXV5MmRqby51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzE4NTQ4MjU5LCJleHAiOjE3MTg2MzQ2NTksInNjb3BlIjoib3BlbmlkIHByb2ZpbGUiLCJhenAiOiJ2cjdyZWxjTGhoUnJ6QUd6cUdYVUlxdkZDR0t0YkE3SyIsInBlcm1pc3Npb25zIjpbInJlYWQ6YXJ0aXN0cyIsInJlYWQ6Z2VucmVzIiwicmVhZDpwbGF5bGlzdHMiLCJyZWFkOnJlbGVhc2VzIiwicmVhZDp0cmFja3MiLCJ3cml0ZTphcnRpc3RzIiwid3JpdGU6Z2VucmVzIiwid3JpdGU6cGxheWxpc3RzIiwid3JpdGU6cmVsZWFzZXMiLCJ3cml0ZTp0cmFja3MiXX0.jA6utAcyc9FukT70oDkTGK1uHCc-qWGoPxpBEcN3Vek8bOFFZOgcAJ5p510js0rWzdZG8Yc7ITn1UotxTpBr4BEl-Q1w8tfxKo2q6_5iKySoBx3sGeujWD20WWNFanEl79Wl8Q6GMRBO1L5u3UlxeO_t7ir-aGePtldOTfEzanYvvZnNQNIg1whV22Z81ty8tPHrnYdzbwddjmJDw7vCmEeFlclJobq1e8HBut8qg5Dkd6-jojxzaFjS0QG0q_5zUj5MgCJxb1-SxI2bXofPp0geSzDtWD9SrOW2A8OFTx4fkjCXJoo8B--pDQlXg2qIRHUs9RUEyDhr0ATvaOfG_Q"
        self.client.verify = False

    def headers(self):
        """
        Returns headers with the Bearer token included
        """
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
