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
import csv

@pytest.fixture
def driver(request):
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    wd = webdriver.Chrome(chrome_options=chrome_options)

    print(wd.capabilities)
    request.addfinalizer(wd.quit)
    return wd

def test_main(driver):
    search_data(driver, 1219)

def search_data(driver, tasknum):
    with open('login_data.txt', 'r') as ld:
        login_data = ld.readline().split(',')
        print(login_data)
    #login
    driver.get('http://jira.it2g.ru/login.jsp')
    driver.find_element_by_id('login-form-username').send_keys(login_data[0])
    driver.find_element_by_id('login-form-password').send_keys(login_data[1])
    driver.find_element_by_id('login-form-submit').click()
    driver.get('http://jira.it2g.ru/issues/?filter=10480')
    sleep(2)
    test = driver.find_element_by_id('advanced-search').get_attribute('value')
    driver.find_element_by_id('advanced-search').clear()
    new_val=f'project = NPA AND issuetype = Bug AND issue in linkedIssues(NPA-{str(tasknum)}) AND status != Закрыт'
    driver.find_element_by_id('advanced-search').send_keys(new_val)
    driver.find_elements_by_class_name('aui-icon')[8].click()
    sleep(2)
    return get_bugs_data(driver)
    
def get_bugs_data(driver):
    bugs, bugnums, sum =[], [], []

    bugs = driver.find_elements_by_class_name('issue-link')
    bugs = [x.text for x in bugs]
    bugs = list(filter(lambda x: x!='', bugs))

    # Разделяем номер бага и тему бага
    sum = [bugs[x] for x in range(1, len(bugs), 2)]
    bugnums = [bugs[x] for x in range(0, len(bugs), 2)]

    # Чистим значение переменной, для уменьшения используемой памяти. Спросить Дениса надо ли так делать?
    bugs = []

    # Статус бага
    # Приоритет бага
    # Исполнитель бага


    #print(bugs)
    print(sum)
    print(bugnums)