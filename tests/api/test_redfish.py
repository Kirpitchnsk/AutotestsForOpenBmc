import pytest
import requests
import logging
import time
import urllib3
from typing import Dict, Any

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('openbmc_tests.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

BASE_URL = "https://127.0.0.1:2443"
USERNAME = "root"
PASSWORD = "0penBmc"
SYSTEM_ENDPOINT = "/redfish/v1/Systems/system"
SSL_VERIFY = False

def wait_for_bmc_ready():
    """Ждем доступности BMC"""
    import socket
    for _ in range(30):  # 30 попыток с интервалом 10 сек = 5 минут
        try:
            with socket.create_connection(("127.0.0.1", 2443), timeout=5):
                return
        except (socket.timeout, ConnectionRefusedError):
            logger.info("BMC not ready, waiting...")
            time.sleep(10)
    pytest.fail("BMC не доступен после 5 минут ожидания")

@pytest.fixture(scope="session")
def auth_session() -> requests.Session:

    wait_for_bmc_ready()

    """Фикстура для аутентификации с обработкой SSL-сертификатов"""
    session = requests.Session()
    session.timeout = 30

    auth_url = f"{BASE_URL}/redfish/v1/SessionService/Sessions"
    
    try:
        response = session.post(
            auth_url,
            json={"UserName": USERNAME, "Password": PASSWORD},
            verify=SSL_VERIFY,
            timeout=30
        )
        response.raise_for_status()
        
        if response.status_code != 201:
            pytest.fail(f"Ошибка аутентификации. Код: {response.status_code}")
        
        session.headers.update({
            "X-Auth-Token": response.headers.get("X-Auth-Token", ""),
            "Content-Type": "application/json"
        })
        logger.info("Успешная аутентификация")
        return session
        
    except requests.exceptions.SSLError as e:
        logger.warning(f"SSL ошибка, пробуем с verify=False: {str(e)}")
        response = session.post(
            auth_url,
            json={"UserName": USERNAME, "Password": PASSWORD},
            verify=False,
            timeout=5
        )
        if response.status_code == 201:
            session.verify = False
            session.headers.update({
                "X-Auth-Token": response.headers.get("X-Auth-Token", ""),
                "Content-Type": "application/json"
            })
            return session
        pytest.fail(f"Не удалось аутентифицироваться даже с verify=False")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при аутентификации: {str(e)}")
        pytest.fail(f"Ошибка аутентификации: {str(e)}")

def test_authentication(auth_session: requests.Session):
    """Тест успешной аутентификации"""
    assert auth_session.headers.get("X-Auth-Token") is not None

def test_system_info(auth_session: requests.Session):
    """Тест получения информации о системе"""
    try:
        response = auth_session.get(
            f"{BASE_URL}{SYSTEM_ENDPOINT}",
            verify=False,
            timeout=5
        )
        response.raise_for_status()
        
        assert response.status_code == 200, "Неверный статус-код"
        
        data = response.json()
        logger.info(f"Получены данные системы: {data}")
        
        assert "Status" in data, "Отсутствует поле Status"
        assert "PowerState" in data, "Отсутствует поле PowerState"
        assert data["PowerState"] in ["On", "Off"], "Недопустимое значение PowerState"
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе информации о системе: {str(e)}")
        pytest.fail(f"Ошибка запроса: {str(e)}")

@pytest.mark.parametrize("power_action, expected_state", [
    ("On", "On"),
    ("GracefulShutdown", "Off"),
], ids=["power_on", "power_off"])
def test_power_management(
    auth_session: requests.Session,
    power_action: str,
    expected_state: str
):
    """Тест управления питанием с обработкой SSL-ошибок"""
    max_wait = 20
    poll_interval = 5
    
    try:
        reset_url = f"{BASE_URL}{SYSTEM_ENDPOINT}/Actions/ComputerSystem.Reset"
        response = auth_session.post(
            reset_url,
            json={"ResetType": power_action},
            verify=SSL_VERIFY,
            timeout=10
        )
    
        expected_codes = {202, 204} 
        assert response.status_code in expected_codes, (
            f"Ожидался статус {expected_codes}, получен {response.status_code}"
        )
        logger.info(f"Команда {power_action} отправлена успешно. Код: {response.status_code}")
        
        start_time = time.time()
        last_state = None
        
        while time.time() - start_time < max_wait:
            try:
                system_response = auth_session.get(
                    f"{BASE_URL}{SYSTEM_ENDPOINT}",
                    verify=SSL_VERIFY,
                    timeout=10
                )
                system_info = system_response.json()
                current_state = system_info.get("PowerState")
                
                if current_state != last_state:
                    logger.info(f"Текущее состояние питания: {current_state}")
                    last_state = current_state
                
                if current_state == expected_state:
                    logger.info(f"Система достигла ожидаемого состояния: {expected_state}")
                    break
                
                time.sleep(poll_interval)
            except requests.exceptions.SSLError:
                system_response = auth_session.get(
                    f"{BASE_URL}{SYSTEM_ENDPOINT}",
                    verify=False,
                    timeout=10
                )
                system_info = system_response.json()
                current_state = system_info.get("PowerState")
                
                if current_state == expected_state:
                    break
                
                time.sleep(poll_interval)
        else:
            pytest.fail(f"Система не достигла состояния {expected_state} за {max_wait} секунд")
        
        assert current_state == expected_state, (
            f"Ожидалось {expected_state}, получено {current_state}"
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка в тесте управления питанием: {str(e)}")
        pytest.fail(f"Тест не выполнен из-за ошибки: {str(e)}")

@pytest.fixture(autouse=True)
def log_test_execution(request):
    """Фикстура для логирования начала/окончания тестов"""
    logger.info(f"Начало теста: {request.node.name}")
    yield
    logger.info(f"Окончание теста: {request.node.name}")
