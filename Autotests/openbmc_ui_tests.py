from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest

@pytest.fixture
def browser():
    driver = webdriver.Chrome()  # Или webdriver.Firefox()
    yield driver
    driver.quit()

def test_successful_login(browser):
    browser.get("https://<BMC_IP>")  # Замените на IP вашего OpenBMC
    
    # Ввод логина и пароля
    username_field = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username_field.send_keys("root")
    
    password_field = browser.find_element(By.ID, "password")
    password_field.send_keys("0penBmc")  # Пароль с цифрой 0 вместо 'o'
    
    # Нажатие кнопки входа
    login_button = browser.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()
    
    # Проверка успешного входа
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Dashboard')]"))
    )
    assert "Dashboard" in browser.title

def test_failed_login(browser):
    browser.get("https://<BMC_IP>")
    
    username_field = browser.find_element(By.ID, "username")
    username_field.send_keys("wrong_user")
    
    password_field = browser.find_element(By.ID, "password")
    password_field.send_keys("wrong_password")
    
    login_button = browser.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()
    
    # Проверка сообщения об ошибке
    error_message = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'alert-danger')]"))
    )
    assert "Invalid username or password" in error_message.text

def test_account_lockout(browser):
    browser.get("https://<BMC_IP>")
    
    for _ in range(3):  # 3 неудачные попытки
        username_field = browser.find_element(By.ID, "username")
        username_field.clear()
        username_field.send_keys("root")
        
        password_field = browser.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys("wrong_password")
        
        login_button = browser.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        WebDriverWait(browser, 2).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'alert-danger')]"))
        )
    
    # Проверка блокировки
    lockout_message = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Account locked')]"))
    )
    assert "Account locked" in lockout_message.text