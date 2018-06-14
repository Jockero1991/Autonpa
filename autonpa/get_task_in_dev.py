from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import pytest
import csv
from openpyxl import load_workbook as lw
from openpyxl import Workbook
from openpyxl.compat import range
from openpyxl.utils import get_column_letter
from test_pyxl_lib import pyxl
import get_feature_bugs as gtb

@pytest.fixture
def driver(request):
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    wd = webdriver.Chrome(chrome_options=chrome_options)

    print(wd.capabilities)
    request.addfinalizer(wd.quit)
    return wd

# вызов функции для отладки выгрузки модуль
def test_main(driver):
    # Создаем пустой ексель с
    df = gtb.cr_file_xls('В разработке.xlsx')

    # логинимся в системе.
    gtb.login(driver)

    # Найти все задачи по фильтру В разработке.
    iss_lst = gtb.get_tasks_list(driver, '10765')

    # Находим данные по каждой задаче и записываем их в итоговую таблицу
    count = 0

    for x in range(len(iss_lst)):
        iss = dev_tsk_data(driver, iss_lst[x])

        # Вызываем функцию записи в файл.
        count = write_to_xls(iss, df, count)


def dev_tsk_data(driver, issue):
    task_res = []
    print(issue)
    sleep(3)
    driver.get(f'http://jira.it2g.ru/browse/{issue}')

    task_res.append(issue)
    task_res.append(str(driver.find_element_by_id('type-val').text))
    task_res.append(str(driver.find_element_by_id('status-val').text))
    task_res.append(str(driver.find_element_by_id('priority-val').text))
    task_res.append(str(driver.find_element_by_id('summary-val').text))
    task_res.append(str(driver.find_element_by_id('assignee-val').text))
    task_res.append(str(driver.find_element_by_id('fixfor-val').text))
    print(task_res)
    return task_res


# Запись в файл эксель данных по задаче и по связанным багам
def write_to_xls(task, df, lr=0):
    headers = [
        '№ задачи Jira',
        'Трекер',
        'Статус',
        'Приоритет',
        'Тема:',
        'Исполнитель',
        'Версия',
        'Количество задач'
    ]


    # # assign the icon set to a rule
    # border = Border(left = Side(border_style = 'double', color = 'FF000000'),
    #                 right = Side(border_style = 'double', color = 'FF000000'),
    #                 top = Side(border_style = 'double', color = 'FF000000'),
    #                 bottom = Side(border_style = 'double', color = 'FF000000'))

    wb = lw(df)
    #ws1 = wb["TEST"]
    ws1 = wb["В разработке"]

    #Есть задача, файл назначения и номер строки (который передаем)
    starts, ends = '', ''
    for row in range(lr+1, lr+2):
        # Запишем заголовки в файл
        starts = f'{get_column_letter(2)}{lr+1}'
        # Вставляем формулу в столбец итого, но если все ровно по столбцам будет ложиться, то этот код не нужен.
        # if lr == 0:
        #     for col in range(0, len(headers)):
                #_ = ws1.cell(column=col+2, row=row, value=headers[col])
                # if col == (len(headers)-1):
                #     _=ws1.cell(column = col+2, row=row+1, value='=СЧЁТЗ(F3:F30)')
        # Записываем данные по задаче
        print(len(headers), len(task))
        for col in range(0, len(headers)-1):
            _ = ws1.cell(column=col+2, row=row+1, value=task[col])

            ends = f'{get_column_letter(len(headers))}{row+1}'
        #print(f'Финальная ячейка: {ends}')

        lr = row
    rang = f'{starts}:{ends}'
    print(rang)
    #gtb.style_range(ws1, rang, border=border)
    #ws1.conditional_formatting.add(rang, border = dxf)
    wb.save(filename = df)
    return lr