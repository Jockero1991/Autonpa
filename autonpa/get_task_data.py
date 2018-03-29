from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains as ac
from selenium.webdriver.common.keys import Keys as ks
from datetime import datetime as dt
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from time import sleep
import pytest

@pytest.fixture
def driver(request):
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    wd = webdriver.Chrome(chrome_options=chrome_options)

    print(wd.capabilities)
    request.addfinalizer(wd.quit)
    return wd

def test_main(driver):
    #login
    driver.get('http://jira.it2g.ru/login.jsp')
    driver.find_element_by_id('login-form-username').send_keys('')
    driver.find_element_by_id('login-form-password').send_keys('')
    driver.find_element_by_id('login-form-submit').click()

    driver.get('http://jira.it2g.ru/issues/?jql=')
    driver.find_element_by_xpath('//*[@class="filter-link"][@data-id="10753"]').click()
    sleep(3)
    #get_data(driver)

def get_data(driver):
    rows=[]
    rows = driver.find_elements_by_class_name('issuerow')

def write_data():
    pass

def read_data():
    pass