from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import pytest
from openpyxl import load_workbook as lw
from openpyxl import Workbook
from openpyxl.compat import range


@pytest.fixture
def driver(request):
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    wd = webdriver.Chrome(chrome_options=chrome_options)

    print(wd.capabilities)
    request.addfinalizer(wd.quit)
    return wd

def cr_file_xls(filename):
   wb = Workbook()
   ws1=wb.active
   ws1.title = "TEST"
   wb.save(filename = filename)
   return filename

def login(driver):
    with open('login_data.txt', 'r') as ld:
        login_data = ld.readline().split(',')
        print(login_data)
    #login
    driver.get('http://jira.it2g.ru/login.jsp')
    driver.find_element_by_id('login-form-username').send_keys(login_data[0])
    driver.find_element_by_id('login-form-password').send_keys(login_data[1])
    driver.find_element_by_id('login-form-submit').click()

# Функция возвращает массив задач по фильтру Готово к тестированию
def get_tasks_in_test(driver):
    # Открываем фильтр Готово к тестированию
    driver.get('http://jira.it2g.ru/issues/?filter=10472')
    issues = driver.find_elements_by_class_name('issue-link')
    issues = [x.text for x in issues]
    issues = list(filter(lambda x: x!='', issues))
    issues = [issues[x] for x in range(0, len(issues), 2)]
    print(issues)
    return issues

test_arr = ['NPA-1219', 'NPA-1429']

# Отсюда вызываем все функции этого модуля
def test_main(driver):
    fn = cr_file_xls("Тестовая таблица.xlsx")
    login(driver)
    tsk_list = []
    counter = 0
    tsk_list = test_arr #get_tasks_in_test(driver)
    for u in range(len(tsk_list)):
        try:
            bgs = search_data(driver, tsk_list[u])
        except:
            print('Связанных багов нет.')
            bgs = []
        iss = tsk_data(driver, tsk_list[u])
        counter = write_to_xls(iss, bgs, fn, counter)


def search_data(driver, tasknum):

    # Открываем фильтр по багам связанным с задачей.
    driver.get('http://jira.it2g.ru/issues/?filter=10480')
    sleep(2)
    driver.find_element_by_id('advanced-search').clear()
    new_val=f'project = NPA AND issuetype = Bug AND issue in linkedIssues({str(tasknum)}) AND status != Закрыт'
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

    return result

# Запись в файл эксель данных по задаче и по связанным багам
def write_to_xls(task, bugs, df, lr=0):
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

    # Запишем заголовки в файл
    wb = lw(df)
    ws1 = wb["В тестировании"]
    
    quan_h = ['Кол-во багов: ', str(len(bugs))]
    #Есть задача, баги, файл назначения и номер строки (который передаем)

    for row in range(lr+1, lr+2):
        for col in range(0, len(headers)):
            _ = ws1.cell(column=col+1, row=row, value=headers[col])
        for col in range(0, len(headers)-7):
            # Записываем данные по задаче
            _ = ws1.cell(column=col+1, row=row+1, value = task[col])
            if(col != len(headers)-7):
                if bugs == []:
                    lr = row+2
                else:
                   # Записываем данные по багам
                   for b in range(1, len(bugs)+1):
                       _ = ws1.cell(column=col+7, row=row+b, value = bugs[b-1][col])
        lr = row+len(bugs)
        for col in range(0, len(quan_h)):
            # Кол-во багов под данныами по задаче
            _ = ws1.cell(column=col+1, row=row+2, value = quan_h[col])

    wb.save(filename = df)
    return lr


# Собираем данные о задаче возвращаем №, приоритет, статус, тему, QA
def tsk_data(driver, issue):
    task_res = []
    print(issue)
    sleep(3)
    driver.get(f'http://jira.it2g.ru/browse/{str(issue)}')

    task_res.append(issue)
    task_res.append(str(driver.find_element_by_id('priority-val').text))
    task_res.append(str(driver.find_element_by_id('status-val').text))
    task_res.append(str(driver.find_element_by_id('summary-val').text))
    task_res.append(str(driver.find_element_by_xpath('//*[@id="customfield_10201-val"]/span').text))
    print(task_res)
    return task_res

