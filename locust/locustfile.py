from locust import HttpUser, task, between


class ApiUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(2)
    def work(self):
        self.client.get("/work")

    @task(1)
    def health(self):
        self.client.get("/health")
