from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import pytest

BMC_URL = "https://localhost:2443/?next=/login#/login"
USERNAME = "root"
PASSWORD = "0penBmc"
INVALID_PASSWORD = "wrongpassword"

@pytest.fixture(scope="module")
def browser():   
    driver = webdriver.Firefox()
    driver.implicitly_wait(2)
    
    yield driver
    driver.quit()

def test_successful_login(browser):
    """Тест успешной авторизации"""
    browser.get(BMC_URL)
    
    username_field = browser.find_element(By.ID, "username")
    password_field = browser.find_element(By.ID, "password")
    login_button = browser.find_element(By.XPATH, "//button[contains(text(), 'Log in')]")
    
    username_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)
    login_button.click()
    
    time.sleep(3)  
    assert "Overview" in browser.title
    assert "Log out" in browser.page_source

def test_invalid_login(browser):
    """Тест авторизации с неверными данными"""
    browser.get(BMC_URL)
    
    username_field = browser.find_element(By.ID, "username")
    password_field = browser.find_element(By.ID, "password")
    login_button = browser.find_element(By.XPATH, "//button[contains(text(), 'Log in')]")
    
    username_field.send_keys(USERNAME)
    password_field.send_keys(INVALID_PASSWORD)
    login_button.click()

    time.sleep(1)
    current_url = browser.current_url
    assert current_url == BMC_URL

def test_account_lockout(browser):
    """Тест блокировки учетной записи после нескольких неудачных попыток"""
    browser.get(BMC_URL)
    
    for _ in range(10): 
        if browser.title == "":
            assert True
        
        else:
            username_field = browser.find_element(By.ID, "username")
            password_field = browser.find_element(By.ID, "password")
            login_button = browser.find_element(By.XPATH, "//button[contains(text(), 'Log in')]")
        
            username_field.clear()
            password_field.clear()
        
            username_field.send_keys(USERNAME)
            password_field.send_keys(INVALID_PASSWORD)
            login_button.click()

            print("https://" + browser.title + " "+ browser.current_url)
    
    if browser.title != "":
        assert False