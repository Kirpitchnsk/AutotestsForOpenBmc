import pytest
import requests
import logging
import time
from requests.auth import HTTPBasicAuth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://127.0.0.1:2443"
USERNAME = "root"
PASSWORD = "0penBmc"
VERIFY_SSL = False

def log_response(response):
    """Логирование деталей запроса и ответа"""
    logger.info(f"Request: {response.request.method} {response.request.url}")
    logger.info(f"Request headers: {response.request.headers}")
    logger.info(f"Response status: {response.status_code}")
    logger.info(f"Response headers: {response.headers}")
    logger.info(f"Response body: {response.text[:200]}...")

@pytest.fixture(scope="module")
def auth_session():
    """Фикстура для аутентифицированной сессии"""
    session = requests.Session()
    session.auth = HTTPBasicAuth(USERNAME, PASSWORD)
    session.verify = VERIFY_SSL
    yield session
    session.close()

def test_authentication(auth_session):
    """Тест аутентификации в OpenBMC"""
    response = auth_session.get(f"{BASE_URL}/redfish/v1")
    log_response(response)
    
    assert response.status_code == 200
    data = response.json()
    assert "RedfishVersion" in data
    
    if "Links" in data:
        assert "Systems" in data["Links"] or "ManagerProvidingService" in data["Links"]
    else:
        assert "Systems" in data or "ManagerProvidingService" in data

@pytest.mark.parametrize("endpoint", [
    "/redfish/v1/Systems",
    "/redfish/v1/Chassis",
    "/redfish/v1/Managers",
    "/redfish/v1/SessionService"
])
def test_redfish_endpoints(auth_session, endpoint):
    """Тестирование доступности основных конечных точек"""
    response = auth_session.get(f"{BASE_URL}{endpoint}")
    log_response(response)
    
    assert response.status_code == 200
    data = response.json()
    assert "@odata.id" in data
    assert "@odata.type" in data

def test_system_info(auth_session):
    """Тест получения информации о системе"""
    response = auth_session.get(f"{BASE_URL}/redfish/v1/Systems/system")
    log_response(response)
    
    data = response.json()
    assert response.status_code == 200
    assert "Status" in data
    assert "PowerState" in data
    assert data["PowerState"] in ["On", "Off"]

def test_invalid_credentials():
    """Тест с неверными учетными данными"""
    with requests.Session() as session:
        session.auth = HTTPBasicAuth("invalid", "credentials")
        session.verify = VERIFY_SSL
        response = session.get(f"{BASE_URL}/redfish/v1")
        log_response(response)
        
        assert "RedfishVersion" in response.json()

def test_unauthorized_access():
    """Тест доступа без аутентификации"""
    response = requests.get(f"{BASE_URL}/redfish/v1", verify=VERIFY_SSL)
    log_response(response)
    
    assert "RedfishVersion" in response.json()

def test_power_management(auth_session):
    """Тест управления питанием"""
    current_state = auth_session.get(
        f"{BASE_URL}/redfish/v1/Systems/system"
    ).json()["PowerState"]
    
    if current_state == "On":
        reset_type = "Graceful Shutdown"
        expected_state = "Off"
    else:
        reset_type = "On"
        expected_state = "On"
    
    response = auth_session.post(
        f"{BASE_URL}/redfish/v1/Systems/system/Actions/ComputerSystem.Reset",
        json={"ResetType": reset_type}
    )
    log_response(response)
    
    assert response.status_code in [200, 204]
    
    timeout = time.time()
    while True:
        time.sleep(2)
        updated_state = auth_session.get(
            f"{BASE_URL}/redfish/v1/Systems/system"
        ).json()["PowerState"]
        
        if updated_state == expected_state or time.time() > timeout:
            break
    
    assert updated_state == expected_state

if __name__ == "__main__":
    pytest.main(["-v", "--html=report.html"])