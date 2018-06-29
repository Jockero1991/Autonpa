from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import pytest
from openpyxl import load_workbook as lw
from openpyxl import Workbook
from openpyxl.compat import range
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, PatternFill, Border, Side
#from openpyxl.formatting.rule import IconSet, FormatObject
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.formatting.rule import Rule
from test_pyxl_lib import style_range


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
    with open('login_data.txt', 'r', encoding='utf-8') as ld:
        login_data = ld.readline().split(',')
        print(login_data)
    #login
    driver.get('http://jira.it2g.ru/login.jsp')
    driver.find_element_by_id('login-form-username').send_keys(login_data[0])
    driver.find_element_by_id('login-form-password').send_keys(login_data[1])
    driver.find_element_by_id('login-form-submit').click()
    return login_data[2]

# Функция возвращает массив задач по фильтру Готово к тестированию
def get_tasks_list(driver, filter_id, sprint):
    # Открываем фильтр Готово к тестированию
    driver.get(f'http://jira.it2g.ru/issues/?filter={filter_id}')
    issues = driver.find_elements_by_class_name('issue-link')
    issues = [x.text for x in issues]
    issues = list(filter(lambda x: x!='', issues))
    issues = [issues[x] for x in range(0, len(issues), 2)]
    correct_iss = []
    
    #Проверка версии у задачи перед записью в файл
    # versions = driver.find_elements_by_class_name('fixVersions')
    # versions = [x.text for x in versions]
    # sprint = sprint.split(',')
    # print(versions)
    # for x in range(len(issues)):
    #     if versions[x] in sprint:
    #         correct_iss.append(issues[x])
    #     else:
    #         temp_ver = versions[x].split(',')
    #         correct_ver = sprint
    #         print(temp_ver)
    #         if len(temp_ver) > 1:
    #             temp_equals, temp_not = [], []
    #             for y in range(len(temp_ver)):
    #                 if temp_ver[y] == correct_ver[y]:
    #                     temp_equals.append(temp_ver[y])
    #                 else:
    #                     temp_not.append(temp_ver[y])
    #             if len(temp_not)>0:
    #                 not_count = 0
    #                 for u in range(len(temp_not)):
    #                     print(temp_not[u])
    #                     res = temp_not[u].find('Release')
    #                     print(res)
    #                     if res:
    #                         not_count += 1
    #                 if not_count == 0:
    #                     correct_iss.append(issues[x])            
    #         else:
    #             if temp_ver[0] == correct_ver[1]:
    #                  correct_iss.append(issues[x])
    #             else:
    #                 print('Уточнить версию: ' + versions[x] + ' у задачи: ' + issues[x])
                
    print(issues)
    return issues
# Масссив для быстрой отладки скрипта для вкладки тестирование
# test_arr = ['NPA-1219', 'NPA-1429']

# Отсюда вызываем все функции этого модуля
def test_main(driver):
    fn = cr_file_xls("Тестовая таблица.xlsx")
    login(driver)
    tsk_list = []
    counter = 0
    tsk_list = get_tasks_list(driver, '10472')
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
        'Статус',
        'Тема:',
        'Тестировщик',
        'Версия',
        'Комментарий', 
        '№ бага', 
        'Тема',  
        'Статус', 
        'Приоритет', 
        'Исполнитель', 
        'Можно перенести']


    # assign the icon set to a rule
    border = Border(left = Side(border_style = 'double', color = 'FF000000'),
                                          right = Side(border_style = 'double', color = 'FF000000'),
                                          top = Side(border_style = 'double', color = 'FF000000'),
                                          bottom = Side(border_style = 'double', color = 'FF000000'))

    wb = lw(df)
    ws1 = wb["В тестировании"]
    
    quan_h = ['Кол-во багов: ', str(len(bugs))]
    #Есть задача, баги, файл назначения и номер строки (который передаем)
    starts, ends = '', ''
    for row in range(lr+1, lr+2):
        # Запишем заголовки в файл
        starts = f'{get_column_letter(2)}{lr+1}'
        for col in range(0, len(headers)):
            _ = ws1.cell(column=col+2, row=row, value=headers[col])

        # Записываем данные по задаче
        print(len(headers), len(task))
        for col in range(0, len(headers)-7):
            _ = ws1.cell(column=col+2, row=row+1, value=task[col])

        for col in range(0, len(headers)-8):
            if(col != len(headers)-8):
                if bugs == []:
                    lr = row+4
                else:
                   # Записываем данные по багам
                   #print(len(headers), len(bugs[1]))
                   for b in range(1, len(bugs)+1):
                        #print(col+8)
                        _ = ws1.cell(column=col+9, row=row+b, value = bugs[b-1][col])
        ends = f'{get_column_letter(len(headers)+1)}{row+(len(bugs)+1)}'
        #print(f'Финальная ячейка: {ends}')
        lr = row+len(bugs)+2
        for col in range(0, len(quan_h)):
            # Кол-во багов под данными по задаче
            _ = ws1.cell(column=col+2, row=row+2, value = quan_h[col])
        print(task[0], quan_h)
    rang = f'{starts}:{ends}'
    print(rang)
    style_range(ws1, rang, border=border)
    #ws1.conditional_formatting.add(rang, border = dxf)
    wb.save(filename = df)
    return lr

def write_quantity_of_task(df, cntr):
    wb = lw(df)
    ws1 = wb["В тестировании"]
    quantity = ['Кол-во задач: ', '=СЧЁТЗ(E1:E99)/2']
    for col in range(0, len(quantity)):
        # Кол-во багов под данными по задаче
        _ = ws1.cell(column=col+2, row=cntr+1, value = quantity[col])
    wb.save(filename = df)

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
    task_res.append(str(driver.find_element_by_id('fixfor-val').text))
    print(task_res)
    return task_res

