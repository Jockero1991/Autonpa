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
from openpyxl import load_workbook as lw
from openpyxl import Workbook
from openpyxl.compat import range
from openpyxl.utils import get_column_letter
from test_pyxl_lib import pyxl

@pytest.fixture
def driver(request):
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    wd = webdriver.Chrome(chrome_options=chrome_options)

    print(wd.capabilities)
    request.addfinalizer(wd.quit)
    return wd

# Фича-лист
# - добавить поле исправлено в версии
# - Кастомизировать выгрузку под каждую вкладку отчета.

filters_npa = [
["10765",  # задачи в разработке
"10766", # задачи в аналитике
"10769", # задачи в тестировании
"10767", # закрытые задачи
"10770", # Открытые баги
"10772", # Закрытые баги
"10773"  # Отложенные задачи
],
 ['data\в_разработке.csv', 'data\в_аналитике.csv',
 'data\в_тестировании.csv',
 'data\закрытые_задачи.csv',
 'data\Открытые_баги.csv', 'data\закрытые_баги.csv', 'data\отложенные задачи.csv'
  ],
  ['В разработке', 'В аналитике',
  'В тестировании',
  'Готовые задачи',
  'Открытые баги', 'Исправленные баги', 'Отложеные,отклоненные'
  ]
 ]

def test_main(driver):
    #login_data=[]
    with open('login_data.txt', 'r') as ld:
        login_data = ld.readline().split(',')
        print(login_data)
    #login
    driver.get('http://jira.it2g.ru/login.jsp')
    driver.find_element_by_id('login-form-username').send_keys(login_data[0])
    driver.find_element_by_id('login-form-password').send_keys(login_data[1])
    driver.find_element_by_id('login-form-submit').click()

    driver.get('http://jira.it2g.ru/issues/?jql=')
    # кликнуть на фильтр 
    for t in range(len(filters_npa[0])):
        generate_report(driver, t)
    
    for z in range(len(filters_npa[1])):
        pyxl(filters_npa[1][z], filters_npa[2][z])


def generate_report(driver, t):
    driver.find_element_by_xpath(f'//*[@class="filter-link"][@data-id="{filters_npa[0][t]}"]').click()
    sleep(4)
    curr_page_count, all_tasks = 0, 0
    table_data = []
    write_data(table_data, filters_npa[1][t], 'headers')
    try:
        all_tasks = driver.find_element_by_class_name('results-count-total').text
        curr_page_count = driver.find_element_by_class_name('results-count-end').text
        if int(curr_page_count) < int(all_tasks):
            while int(curr_page_count) < int(all_tasks):
                table_data = get_data(driver)
                # Записываем в файл добытые данные...
                write_data(table_data, filters_npa[1][t], 'data')
                #print(table_data[0])
                driver.execute_script('$(".icon-next").click()')
                sleep(2)
                all_tasks = driver.find_element_by_class_name('results-count-total').text
                curr_page_count = driver.find_element_by_class_name('results-count-end').text
        if int(curr_page_count) == int(all_tasks):
            table_data = get_data(driver)
            # Записываем в файл добытые данные...
            write_data(table_data, filters_npa[1][t], 'data', True)
            
    except:
        print('нет счетчика задач, задач тоже нет')
        
    # Проверяем содержимое файла...
    #read_data(filters_npa[1][t], table_data)

def get_data(driver):
    types_of_tasks = []
    task_id=[]
    summary=[]
    assignee=[]
    assigned = []
    statuses, priority = [], []
    qa_assigned = []
    qa = []
    result = []
    print('Функция запустилась!')
    try:
        types_of_tasks = driver.find_elements_by_class_name('issuetype')
        types_of_tasks = [x.find_element_by_tag_name('img').get_attribute('alt') for x in types_of_tasks]
    
        task_id = driver.find_elements_by_class_name('issuekey')
        task_id = [x.find_element_by_tag_name('a').text for x in task_id]
    
        summary = driver.find_elements_by_class_name('summary')
        summary = [x.find_element_by_tag_name('p').text for x in summary]

        statuses = driver.find_elements_by_class_name('status')
        statuses = [x.find_element_by_tag_name('span').text for x in statuses]

        priority = driver.find_elements_by_class_name('priority')
        priority = [x.find_element_by_tag_name('img').get_attribute('alt') for x in priority]
        #print(priority)
    
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
            temp_str = f'{task_id[r]}|{types_of_tasks[r]}|{statuses[r]}|{priority[r]}|{summary[r]}|{assignee[r]}|{qa_assigned[r]}'.split(',')
            result.append(temp_str)
        print(result[0])
        return result
    except:
        print('Задач нет')
        return ''
# Переписать функцию, чтобы писала сразу в excel для каждой вкладки свои данные
def write_data(data, path, trigger='headers', end = False):
    # в случае trigger = 'headers' в файл записывается строчка с заголовками столбцов
    # в случае trigger = 'data' в файл записываются данные с задачами
    with open(path, "a", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')

        if trigger=='headers':
            writer.writerow('№ в Jira|Тип задачи|Статус|Приоритет|Тема|Исполнитель|Тестировщик'.split(','))

        if trigger == 'data':
            for line in data:
                writer.writerow(line)
        if end:
            csv_file.close()

def read_data(path, assert_data):
    reading_txt=[]
    with open(path, "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        #print(reader[0])
        for line in reader:
            reading_txt.append(line["№ в Jira|Тип задачи|Статус|Приоритет|Тема|Исполнитель|Тестировщик"])
    
    for x in range(len(reading_txt)):
        assert reading_txt[x] == assert_data[x][0]