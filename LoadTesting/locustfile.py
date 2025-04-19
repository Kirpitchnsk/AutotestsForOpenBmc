from locust import HttpUser, task, between
import random

class OpenBMCUser(HttpUser):
    wait_time = between(1, 3)  # Интервал между запросами (сек)
    host = "https://127.0.0.1:2443"  # Замените на IP вашего OpenBMC
    
    def on_start(self):
        """Аутентификация при старте пользователя"""
        self.client.verify = False  # Отключаем проверку SSL
        self.client.auth = ("root", "0penBmc")  # Учетные данные
    
    @task(3)  # Частота выполнения (относительно других задач)
    def get_system_info(self):
        """Запрос информации о системе"""
        with self.client.get("/redfish/v1/Systems/system", catch_response=True) as response:
            if response.status_code == 200:
                # Проверяем обязательные поля в ответе
                if not all(k in response.json() for k in ["PowerState", "Status"]):
                    response.failure("Missing required fields in response")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def get_manager_info(self):
        """Запрос информации о BMC"""
        self.client.get("/redfish/v1/Managers/bmc")
    
    @task(1)
    def power_operation(self):
        """Операция управления питанием"""
        current_state = self.client.get("/redfish/v1/Systems/system").json()["PowerState"]
        
        if current_state == "On":
            reset_type = "Graceful Shutdown"
        else:
            reset_type = "On"
        
        with self.client.post(
            "/redfish/v1/Systems/system/Actions/ComputerSystem.Reset",
            json={"ResetType": reset_type},
            catch_response=True
        ) as response:
            if response.status_code not in [200, 202]:
                response.failure(f"Unexpected status: {response.status_code}")
    
    @task(1)
    def get_sensors(self):
        """Запрос данных датчиков"""
        self.client.get("/redfish/v1/Chassis/chassis/Sensors")