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
from openpyxl import load_workbook as lw
from openpyxl import Workbook
from openpyxl.compat import range
from openpyxl.utils import get_column_letter

@pytest.fixture
def driver(request):
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    wd = webdriver.Chrome(chrome_options=chrome_options)

    print(wd.capabilities)
    request.addfinalizer(wd.quit)
    return wd

def test_main(driver):
    bgs = search_data(driver, 1219)
    iss = tsk_data(driver, 'NPA-1219')
    write_to_xls(iss, bgs)


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
    bugs, bugnums, summ =[], [], []

    bugs = driver.find_elements_by_class_name('issue-link')
    bugs = [x.text for x in bugs]
    bugs = list(filter(lambda x: x!='', bugs))

    # Разделяем номер бага и тему бага
    summ = [bugs[x] for x in range(1, len(bugs), 2)]
    bugnums = [bugs[x] for x in range(0, len(bugs), 2)]

    # Статус бага
    stat = driver.find_elements_by_class_name('status')
    stat = [x.text for x in stat]

    # Приоритет бага
    pr = driver.find_elements_by_xpath('//*[@class="priority"]/img')
    pr = [x.get_attribute('alt') for x in pr]

    # Исполнитель бага
    assign = driver.find_elements_by_class_name('assignee')
    assign = [x.text for x in assign]
    
    # Объединить данные в один массив
    result = [[] for x in range(len(bugnums))]
    # print(len(bugnums))
    
    for y in range(len(bugnums)):
        result[y].append(bugnums[y])
        result[y].append(summ[y])
        result[y].append(stat[y])
        result[y].append(pr[y])
        result[y].append(assign[y])         

    #Результаты в консоли
    #print(result)

    return result

# Запись в файл эксель данных по задаче и по связанным багам
def write_to_xls(task, bugs):
    headers = [
        '№ задачи Jira', 
        'Приоритет',
        'Тема:', 
        'Статус', 
        'Тестировщик', 
        'Комментарий', 
        '№ бага', 
        'Тема',  
        'Статус', 
        'Приоритет', 
        'Исполнитель', 
        'Можно перенести']
    # Файл назовем как-нибудь
    file_name = 'Тестовая таблица.xlsx'
    # Запишем заголовки в файл
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "TEST"
    for row in range(2, 3):
        for col in range(0, len(headers)):
            _ = ws1.cell(column=col+1, row=row, value=headers[col])
    for row in range(3, 4):
        for col in range(0, len(headers)-7):
            print(len(headers), len(task))        
            _ = ws1.cell(column=col+1, row=row, value = task[col])
            for b in range(len(bugs)):
                _ = ws1.cell(column=col+7, row=row+b, value = bugs[b][col])
    wb.save(filename = file_name)


# Собираем данные о задаче возвращаем №, приоритет, статус, тему, QA
def tsk_data(driver, issue):
    task_res = []
    driver.get(f'http://jira.it2g.ru/browse/{issue}')
    task_res.append(issue)
    task_res.append(str(driver.find_element_by_id('priority-val').text))
    task_res.append(str(driver.find_element_by_id('status-val').text))
    task_res.append(str(driver.find_element_by_id('summary-val').text))
    task_res.append(str(driver.find_element_by_xpath('//*[@id="customfield_10201-val"]/span').text))
    print(task_res)
    return task_res

