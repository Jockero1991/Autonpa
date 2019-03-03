from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
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
import get_feature_bugs as gtb
import get_task_in_dev as gtid
import datetime


# chrome_options = Options()
# chrome_options.add_argument("--window-size=1920,1080")
# caps=DesiredCapabilities.CHROME
# caps['loggingPrefs']={'browser': 'ALL'}


@pytest.fixture
def driver(request):
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    wd = webdriver.Chrome(chrome_options=chrome_options)

    print(wd.capabilities)
    request.addfinalizer(wd.quit)
    return wd


filters_npa = [
["10765",  # задачи в разработке
 "10769", # задачи в тестировании
"10766", # задачи в аналитике
"10767", # закрытые задачи
"10770", # Открытые баги
"10772", # Закрытые баги
"10773"  # Отложенные задачи
],
 [
 'data\в_аналитике.csv',
 'data\закрытые_задачи.csv',
 'data\Открытые_баги.csv', 'data\закрытые_баги.csv', 'data\отложенные задачи.csv'
  ],
  ['В разработке',
   'В тестировании',
   'В аналитике',
  'Готовые задачи',
  'Открытые баги', 'Исправленные баги', 'Отложеные,отклоненные'
  ]
 ]

test_arr = ['NPA-1219', 'NPA-1429']
mode = ['proj_status', 'bugs']



# Необходимые доработки:
# устранить убогое отображение задач для кейса, когда нет задач в аналитике/разработке/тестировании
# убрать пустую строчку, если в аналитике или в разработке нет задач



def test_new_main(driver):
    all_issues = []
    counter = 0
    fn, page ='', ''
    pr_data = gtb.login(driver)
    print(pr_data)

    for r in range(len(pr_data)):
        all_issues=[]
        counter = 0
        if 'bugs' in pr_data[r]:
            pass # это комментировать когда запускаем отчет по багам и убирать комментирование с блока внизу.
            # fn = gtb.cr_file_xls("data\\" + "Список дефектов ИС УСД ПМ " + str(datetime.date.today()) + ".xlsx")
            # print(fn)
            # page = fn[1]
            # fn = fn[0]
            # filters_ids=[pr_data[r][x] for x in range(2, len(pr_data[r]))]
            # print(filters_ids)
            # all_issues = gtb.get_tasks_list(driver, filters_ids[0],'','bugs')
            # print(all_issues)
            # for y in range(len(all_issues)):
            #     print(all_issues[y])
            #     task_details = gtid.dev_tsk_data(driver, all_issues[y], 'bugs')
            #     counter = gtid.write_to_xls(task_details, fn, page, counter, 'bugs')
        else:
            if 'proj_status' in pr_data[r]:
                fn = gtb.cr_file_xls("data\\" + pr_data[r][0] + "_Отчет за " + str(datetime.date.today()) + ".xlsx")
                print(fn)
                page = fn[1]
                fn = fn[0]
                filters_ids=[pr_data[r][x] for x in range(3, len(pr_data[r]))]
                print(filters_ids)

                driver.get('http://jira.it2g.ru/issues/?jql=')

                for x in range(len(filters_ids)):
                    if x == 0:
                        all_issues.append('В аналитике')
                    if x == 1:
                        all_issues.append('В разработке')
                    if x == 2:
                        all_issues.append('В тестировании')
                    temp_issues = gtb.get_tasks_list(driver, filters_ids[x], pr_data[0][1])
                    all_issues.append(temp_issues)
                print(all_issues)
                for y in range(len(all_issues)):
                    if type(all_issues[y]) is str:
                        #print(all_issues[y])
                        counter = gtid.write_to_xls(all_issues[y], fn, page, counter)
                    else:
                        for z in range(len(all_issues[y])):
                            print(all_issues[y][z])
                            task_details = gtid.dev_tsk_data(driver, all_issues[y][z])
                            counter = gtid.write_to_xls(task_details, fn, page, counter)
                #print(all_issues[y])




