from locust import HttpUser, task, between, LoadTestShape
import json

class OpenBMCTest(HttpUser):
    """Тестирование OpenBMC API"""
    wait_time = between(1, 3)
    host = "http://127.0.0.1:2443"

    @task
    def get_system_info(self):
        with self.client.get("/redfish/v1/Systems/system", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    if response.json().get("PowerState"):
                        response.success()
                    else:
                        response.failure("Missing PowerState")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON")
            else:
                response.failure(f"Status {response.status_code}")

class PublicAPITest(HttpUser):
    """Тестирование публичного API"""
    wait_time = between(3, 5)
    host = "https://jsonplaceholder.typicode.com"

    @task(weight=3)
    def get_weather(self):
        with self.client.get("https://wttr.in/Novosibirsk?format=j1", name="weather", catch_response=True) as response:
            if not response.json().get("current_condition"):
                response.failure("Invalid weather format")

    @task
    def get_posts(self):
        self.client.get("/posts")

class StepLoadShape(LoadTestShape):
    """
    План нагрузки с постепенным увеличением:
    1. 10 пользователей на 60 сек
    2. 50 пользователей на 120 сек
    3. 100 пользователей на 180 сек
    4. 200 пользователей до конца теста
    """
    
    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 5},
        {"duration": 120, "users": 50, "spawn_rate": 10},
        {"duration": 180, "users": 100, "spawn_rate": 15},
        {"duration": 240, "users": 200, "spawn_rate": 20},
    ]

    def tick(self):
        run_time = self.get_run_time()
        
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
        
        return (self.stages[-1]["users"], self.stages[-1]["spawn_rate"])