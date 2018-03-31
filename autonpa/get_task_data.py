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

filters_npa = [
 ["10765", # задачи в разработке
 "10766", # задачи в аналитике
 "10769", # задачи в тестировании
 "10767", # закрытые задачи
 "10770", # Открытые баги 
 "10772"], # Закрытые баги
 ['в_разработке.csv', 'в_аналитике.csv', 'в_тестировании.csv', 'закрытые_задачи.csv', 'Открытые_баги.csv', 'закрытые_задачи.csv']
 ]

def test_main(driver):
    #login
    driver.get('http://jira.it2g.ru/login.jsp')
    driver.find_element_by_id('login-form-username').send_keys('')
    driver.find_element_by_id('login-form-password').send_keys('')
    driver.find_element_by_id('login-form-submit').click()

    driver.get('http://jira.it2g.ru/issues/?jql=')
    # кликнуть на фильтр 
    for t in range(len(filters_npa[0])):
        generate_report(driver, t)


def generate_report(driver, t):
    driver.find_element_by_xpath(f'//*[@class="filter-link"][@data-id="{filters_npa[0][t]}"]').click()
    sleep(2)
    # Добываем данные...
    table_data = get_data(driver)
    # Записываем в файл добытые данные...
    write_data(table_data, filters_npa[1][t])
    # Проверяем содержимое файла...
    read_data(filters_npa[1][t], table_data)

def get_data(driver):
    types_of_tasks = []
    task_id=[]
    summary=[]
    assignee=[]
    assigned = []
    statuses = []
    qa_assigned = []
    qa = []
    result = []
    try:
        types_of_tasks = driver.find_elements_by_class_name('issuetype')
        types_of_tasks = [x.find_element_by_tag_name('img').get_attribute('alt') for x in types_of_tasks]
    
        task_id = driver.find_elements_by_class_name('issuekey')
        task_id = [x.find_element_by_tag_name('a').text for x in task_id]
    
        summary = driver.find_elements_by_class_name('summary')
        summary = [x.find_element_by_tag_name('p').text for x in summary]

        statuses = driver.find_elements_by_class_name('status')
        statuses = [x.find_element_by_tag_name('span').text for x in statuses]
    
        assignee = driver.find_elements_by_class_name('assignee')
        qa_assigned = driver.find_elements_by_css_selector('.customfield_10201')
    
        for u in range(len(assignee)):
            try:
                assigned.append(assignee[u].find_element_by_css_selector(' span a').text)
            except:
                assigned.append(assignee[u].find_element_by_tag_name('em').text)
            try:
                qa.append(qa_assigned[u].find_element_by_css_selector('span a').text)
            except:
                qa.append('Не назначен')
        
            assignee[u] = assigned[u]
            qa_assigned[u] = qa[u]
        temp_str = '' 
  
        for r in range(len(types_of_tasks)):
            temp_str = f'{task_id[r]}|{types_of_tasks[r]}|{statuses[r]}|{summary[r]}|{assignee[r]}|{qa_assigned[r]}'.split(',')
            result.append(temp_str)
        return result
    except:
        return ''

def write_data(data, path):
    with open(path, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow('№ в Jira|Тип задачи|Статус|Тема|Исполнитель|Тестировщик'.split(','))
        for line in data:
            writer.writerow(line)

def read_data(path, assert_data):
    reading_txt=[]
    with open(path, "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        #print(reader[0])
        for line in reader:
            reading_txt.append(line["№ в Jira|Тип задачи|Статус|Тема|Исполнитель|Тестировщик"])
    
    for x in range(len(reading_txt)):
        assert reading_txt[x] == assert_data[x][0]