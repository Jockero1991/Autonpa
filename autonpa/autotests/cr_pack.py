#####################################################################################
#                               ИМПОРТЫ                                             #
# pip3 install py-postgresql                                                                                  #
# импортируем selenium.webdriver                                                    #
# импортируем модуль Опции браузера Хром.                         #
# предварительно его скачиваем, например используя pip.exe install selenium         #
# импортируем модуль для эмуляции клавиатурного ввода                               #
# импортируем модуль os из стандартной библиотеки для работы с операционкой.        #
# импортируем модуль для работы со временем и датой - например писать в логи время. #
# для ожидания загрузки страницы                                                    #
# для работы с select-списками html                                                 #
# пауза                                                                             #
# рендом                                                                            #
# парсер ini-файла                                                                  #
# строковые константы                                                               #
#                                                                                   #
# pytractor provides utilities for testing Angular.js applications with             #
# selenium for Python. Selenium webdrivers are extended with functionality for      #
# dealing with Angular.js applications.                                             #
# pytractor uses scripts provided by protractor (the javascript testing framework   #
# for Angular.js).                                                                  #
#                                                                                   #
# C:\work\Python\Scripts>pip.exe install pytractor                                  #
# C:\work\Python\Scripts>pip.exe install selenium-requests                          #
# Extends Selenium WebDriver classes to include the request function from           #
# the Requests library, while doing all the needed cookie and request headers       #
# handling.                                                                         #
#####################################################################################

import postgresql as ps
from selenium import webdriver as wd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains as ac
from selenium.webdriver.common.keys import Keys as ks
from datetime import datetime as dt
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from time import sleep
import os
import random
import configparser
import string
import sys
from datetime import datetime, date, time

# открываем файл конфига (input.ini)
config = configparser.ConfigParser()
config.read('input.ini')
my_vars = config['VARIABLES']

class MySelenium:
    """ Класс для методов работы с web """
    
    def waiting(condition, locating, locator, timeout, is_visible=0):
        """ функция ожидания элемента на странице или проверка видимости """
        
        ####
        #Код в комментах ниже - это упрощенный пример функции waiting - для понимания.
  #       from selenium.webdriver.support import expected_conditions as EC
		# wait = WebDriverWait(driver, 10)
		# element = wait.until(EC.element_to_be_clickable((By.ID,'someid')))
        ####

        correct_conditions = (
            'title_is', 
            'title_contains', 
            'presence_of_element_located', 
            'visibility_of_element_located', 
            'visibility_of', 
            'presence_of_all_elements_located', 
            'text_to_be_present_in_element', 
            'text_to_be_present_in_element_value', 
            'frame_to_be_available_and_switch_to_it', 
            'invisibility_of_element_located', 
            'element_to_be_clickable', 
            'staleness_of', 
            'element_to_be_selected', 
            'element_located_to_be_selected', 
            'element_selection_state_to_be', 
            'element_located_selection_state_to_be', 
            'alert_is_present'
        )

        correct_locating = (
            'ID', 
            'XPATH', 
            'LINK_TEXT', 
            'PARTIAL_LINK_TEXT', 
            'NAME', 
            'TAG_NAME', 
            'CLASS_NAME', 
            'CSS_SELECTOR'
        )

        if not (condition in correct_conditions):
            myExit("Передан неверный параметр: condition")

        if not (locating in correct_locating):
            myExit("Передан неверный параметр: locating")  

        if not(0 < timeout <= 180):
            myExit("Передан неверный параметр: timeout, диапазон от 1 до 180")

        if not(0 < len(str(locator)) <= 255):
            myExit("Передан неверный параметр: locator, диапазон от 1 символа до 255")
               
        _condition = getattr(EC, condition)
        _locating = getattr(By, locating)

        myLogging(f, 'condition: '+str(condition)+', locating: '+str(locating)+', locator: '+str(locator))
        
        if is_visible:
            try:
                wait = WebDriverWait(driver, timeout)
                element = wait.until(_condition((_locating, locator)))
                return True
            except:
                return False
        else:
            try:
                wait = WebDriverWait(driver, timeout)
                element = wait.until(_condition((_locating, locator)))
            except:
                myLogging(f, ' Элемента не обнаружено. \r\n condition: '+str(condition)+' \r\n locating: '+str(locating)+'\r\n locator: '+str(locator)+' \r\n timeout: '+str(timeout))
                #myExit()
            else:
                return element

def myLogging(file, log_string, time=1, pause=0):
    """ функция логирования выполнения скрипта. Аргументы - указатель на файл, строка для лога, необязательный параметр - нужно ли текущее время. """
    
    dtn=dt.now()
    dtnf = dtn.strftime('%d.%m.%Y %H:%M:%S')

    if len(sys.argv) > 1:
        if sys.argv[1] == 'p':
            pause = 1
    
    if time:
        log_str = dtnf+'\t'+log_string+'\n\r'
    else:
        log_str = log_string+'\n\r'
        
    file.write(log_str)
    print(log_str)
    if pause:
        input()

def myExit(text=''):
    """ Функция коректного выхода из автотеста - логирование, скриншоты, закрытие драйвера и файлов."""
    
    dtn=dt.now()
    dtnf = dtn.strftime('%Y.%m.%d_%H.%M.%S')
    driver.save_screenshot(scrnp+dtnf+"_screen.png")
    myLogging(f, "myExit() function call: "+text)
    f.close()
    try:
        r.close()
    except:
        pass
    driver.quit()
    sys.exit()

f = open(my_vars['log'], 'w')
#scrnp = my_vars['scrn']



# Выпадающие списки
menu_item = '//*[@id="create_list"]'

dd_list = [
'//*[@id="type-project__result"]', # Тип проекта
'//*[@id="status-project__result"]', # Статус
'//*[@id="aproval-form__result"]', # Формат утверждения
'//*[@id="review-type__result"]'# Тип рассмотрения
]

format_u = ['//*[@id="aproval-form__list"]/div[1]' # Заседание ПМ
]

review_type=[
    '//*[@id="review-type__list"]/div[1]' # Открытая повестка
]

# Типы НПА значения списка 1-й вариант
types_npa1 = ['//*[@id="creating-pack-package-of-document"]' #пакет документа
]

# Типы проектов значения списка dd_list[1]
types_proj = ['//*[@id="type-project__list"]/div[1]' # Постановление ПМ
]
# Статусы значения списка dd_list[2]
statuses = ['//*[@id="status-project__list"]/div[1]' # Плановый
]

s_spravoch = [['DOCUMENT_PACKAGE', 'REPORT', 'ABOUT_MAKING_CHANGES'], # - значения типов проектов в БД
[1, 2, 3, 4, 5, 6], # - значения типов проектов в БД
[1, 2, 3, 4], # - значения статусов в БД.
[1, 2, 3, 4], # - значения формата утверждения в БД
[1, 2, 3, 4, 5]] # Тип рассмотрения в БД

# путь к драйверу для хрома, необходимая связка между хромом и вебдрайвером
# скачать у гугла можно
chromedriver = my_vars['chrome']
myLogging(f, chromedriver)
ms = MySelenium

# добавляем данный путь в переменные среды
# иначе будет ошибка: "ChromeDriver executable needs to be available in the path"
os.environ['webdriver.chrome.driver'] = chromedriver

# инициализируем веб-драйвер (открывается Chrome)
myLogging(f, 'Открываем Chrome')
chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")

#driver = wd.Chrome(chrome_options=chrom e_options)

# функция заполнения выпадающих списков
def dropdown_feeler(dropdown, value, exp_DB):
	# кликаем по выпадающему списку
	ms.waiting('element_to_be_clickable', 'XPATH', dropdown, 2, 0).click()
	# кликаем по значению в выпадающем списке
	ms.waiting('element_to_be_clickable', 'XPATH', value, 2, 0).click()
	return exp_DB

def cr_pack_init(path=0, pt=0):
    expected_DB_value = s_spravoch[0][path]
    print(expected_DB_value)
    element = ms.waiting('element_to_be_clickable', 'XPATH', menu_item, 2, 0)
    hov = ac(driver).move_to_element(element)
    hov.perform()
    sleep(0.1)
    ms.waiting('element_to_be_clickable', 'XPATH', types_npa1[pt], 2, 0).click()
    return expected_DB_value


# отдельный метод для нажатия на Ок в алерте.
def alert_passer():
    # Нажать на Ок в поп-ап
    sleep(3)
    try:
        alert = driver.switch_to_alert()
        if alert.text == "Данные сохранены успешно":
            print(alert.text)
            alert.accept()
            return True
        else:
            print("Пакет не сохранен: " + alert.text)
            alert.accept()
            return False
    except:
        print('no any alerts')
        return False

# Составить список ожидаемых значений
# Передать его в метод db_check 
# Функция делает запросы в БД проверяет полученные значения
# Возвращает список пройденных и непройденных тестов

scenario_1 = [
[1, 'page', 'http://npa-tst.it2g.ru/main/dashboard'], #открыть страницу [тип элемента, url]
[2, 'oib', 'npaadmin', '123456'], #login
[3, 'new_pack', 0, 0], # инициировать создание пакета первым способом с первым значением.
[4, 'button', 'save', '//*[@id="save-button"]'], # Нажать Сохранить с пустыми обязательными полями
[5, 'pop-up', 'error', 'popup-alert__field', 'Тип проекта', 'Статус', 'Наименование', 
    'middle-button'], # Поп-ап со списком незаполненных обязательных полей.
[6, 'dropdown', dd_list[0], types_proj[0], s_spravoch[1][0]], # заполняем тип прокта
[7, 'button', 'save', '//*[@id="save-button"]'], # Нажать Сохранить
[8, 'pop-up', 'error', 'popup-alert__field', 'Статус', 'Наименование', 
    'middle-button'], # Поп-ап со списком незаполненных обязательных полей.
[10, 'dropdown', dd_list[1], statuses[0], s_spravoch[2][0]],# заполняем статус
[11, 'button', 'save', '//*[@id="save-button"]'], # Нажать Сохранить
[12, 'pop-up', 'error', 'popup-alert__field', 'Наименование', 
    'middle-button'], # Поп-ап со списком незаполненных обязательных полей.
[13, 'text', '//*[@id="name"]', 'Постановление Правительства Москвы № 102390481'], # Заполнить поле наименование
[14, 'button', 'save', '//*[@id="save-button"]'], # Нажать Сохранить
[15, 'alert'], #закрыть алерт.
[16, 'check_db', 'main'] # получить учетный номер.
]

scenario_2 = [ # создание пакета с 3-мя обязательными полями: Тип проекта, Статус, Наименование
    [0, 'page', 'http://npa-tst.it2g.ru/main/dashboard'],
    [1, 'oib', 'npaadmin', '123456'], # вводим логин и пароль
    [2, 'new_pack', 0, 0], # инициируем создание пакета.
    [3, 'dropdown', dd_list[0], types_proj[0], s_spravoch[1][0]], # заполняем тип прокта
    [4, 'dropdown', dd_list[1], statuses[0], s_spravoch[2][0]],  # заполняем статус
    [5, 'text', '//*[@id="name"]', 'Постановление Правительства Москвы № 102390481'], # заполняем наименование 
    [6, 'button', 'save', '//*[@id="save-button"]'], # нажимаем Сохранить
    [7, 'alert'], # ищем алерт, считываеем и проверяем текст алерта, нажимаем ок.
    [8, 'check_db', 'main'] # проверить данные в бд только 3 обязательных поля.
]

scenario_3 = [ # создание пакета с 3-мя обязательными полями: Тип проекта, Статус, Наименование
    [0, 'page', 'http://npa-tst.it2g.ru/main/dashboard'],
    [1, 'oib', 'npaadmin', '123456'], # вводим логин и пароль
    [2, 'new_pack', 0, 0], # инициируем создание пакета.
    [3, 'dropdown', dd_list[0], types_proj[0], s_spravoch[1][0]], # заполняем тип прокта
    [4, 'dropdown', dd_list[1], statuses[0], s_spravoch[2][0]],  # заполняем статус
    [5, 'text', '//*[@id="name"]', 'Постановление Правительства Москвы № 102390481'], # заполняем наименование 
    [6, 'dropdown', dd_list[2], format_u[0], s_spravoch[3][0]], # Выбираем формат утверждение Заседание ПМ
    [7, 'datapicker', '//*[@id="planedReviewDate"]', 1], # Заполняем планируемую дату рассмотрения 
    [8, 'text', '//*[@id="reviewReason"]', 'Рассмотрение необходимо провести для соблюдения поправки в законе о постановлениях правительства Мэрии г. Москвы.'], # Заполняем обоснование рассмотрение
    [9, 'button', 'add-review', '//*[@id="add-review"]'], # Добавляем рассмотрение
    [10, 'datapicker', '//*[@id="summonsDate"]', 2], # Заполняем дату повестки
    [11, 'dropdown', dd_list[3], review_type[0], s_spravoch[4][0]], # Выбираем тип рассмотрения
    [12, 'button', 'save', '//*[@id="save-button"]'], # нажимаем Сохранить
    [13, 'alert'], # ищем алерт, считываеем и проверяем текст алерта, нажимаем ок.
    [14, 'check_db', 'main', 'review-date', 'subpoena-date'] # проверить данные в бд только 3 обязательных поля.
    ] 




# возникла необходимость вызывать функцию с помощью колбэков и анонимных функций lambda
# вариант 1: массив callback с вызовами функции negative с параметрами строками массива scenario_1
# вариант 2: использовать анонимные функции 
# Отложено!
def negative(sc):
    stack_result = []
    stack_errors = []
    exp_values = []
    for x in range(len(sc)):
        for y in range(len(sc[x])):

            if sc[x][y] =='oib':
                ms.waiting('presence_of_element_located', 'CSS_SELECTOR', '#id3 > div:nth-child(3) > input', 2, 0).send_keys(sc[x][y+1])
                ms.waiting('presence_of_element_located', 'CSS_SELECTOR', '#id1', 2, 0).send_keys(sc[x][y+2])
                ms.waiting('presence_of_element_located', 'CSS_SELECTOR', '#id2', 2, 0).click()

            if sc[x][y] == 'page':
                driver.get(sc[x][y+1])
            
            if sc[x][y] == 'new_pack':
                exp_values.append(cr_pack_init(sc[x][y+1], sc[x][y+2]))    
            if sc[x][y] == 'button':
                print('Нажать кнопку Сохранить')
                ms.waiting('element_to_be_clickable', 'XPATH', sc[x][y+2], 2, 0).click()
            
            if sc[x][y] == 'dropdown':
                exp_values.append(dropdown_feeler(sc[x][y+1], sc[x][y+2], sc[x][y+3]))

            if sc[x][y] == 'text':
                exp_values.append(sc[x][y+2])
                ms.waiting('presence_of_element_located', 'XPATH', sc[x][y+1], 2, 0).send_keys(sc[x][y+2])
            
            if sc[x][y] == 'datapicker':
                print(type(sc[x][y+2]))
                driver.find_elements_by_class_name('btnpickerenabled')[int(sc[x][y+2])].click()
                driver.find_elements_by_class_name('datevalue')[5].click()
                driver.find_elements_by_class_name('datevalue')[5].click()
                # driver.execute_script('$(".btnpickerenabled").click()')
                # driver.execute_script('$(".daycell").click()')
                #ms.waiting('element_to_be_clickable', 'XPATH', sc[x][y+1], 2, 0).send_keys(sc[x][y+2])

            if sc[x][y] == 'pop-up' and sc[x][y+1] == 'error':
                exp = []
                exp = [sc[x][o] for o in range(y+3, (len(sc[x])-1))]
                errors = driver.find_elements_by_class_name(sc[x][y+2])
                print(exp, errors)
                for i in range(len(errors)):
                    #print(errors[i].text)
                    if errors[i].text == exp[i]:
                        print('Поле ' + errors[i].text + ': ок' + '\n Шаг ' + str(sc[x][0]))
                        stack_result.append(1)
                    else:
                        stack_errors.append('Не пройден шаг ' + str(sc[x][0]))
                        print('Поле ' + errors[i].text + ': не ок' + '\n Шаг ' + str(sc[x][0]))
                ms.waiting('element_to_be_clickable', 'CLASS_NAME', sc[x][-1], 2, 0).click()

            if sc[x][y] == 'alert':
                if alert_passer():
                    pass
                else:
                    print('Тест провалился при проверке текста алерта')
            if sc[x][y] == 'check_db':
                db_value = []
                exp_values.append(ms.waiting('presence_of_element_located', 'XPATH', "/html/body/app-root/app-documents/div/div[2]/div[1]/div/div[1]/span", 2, 0).text)
                print(exp_values[len(exp_values) - 1])
                if 'main' in sc[x]:
                    with ps.open('pq://npa:npa@172.17.21.166:5432/npa') as db:
                        db_value.append(db.query("SELECT count(*) FROM document_package WHERE document_package_number = '%s'" % exp_values[len(exp_values) - 1])[0][0]) # Считаем кол-во пакетов с таким же учетным номером
                        db_value.append(db.query("SELECT package_type FROM document_package WHERE document_package_number = '%s'" % exp_values[len(exp_values) - 1])[0][0]) # Тип пакета
                        db_value.append(db.query("SELECT n.project_type_id FROM npa n left join document_package dp on n.document_package_id=dp.id where dp.document_package_number = '%s'" % exp_values[len(exp_values) - 1])[0][0]) # Тип проекта
                        db_value.append(db.query("SELECT n.status FROM npa n left join document_package dp on n.document_package_id=dp.id where dp.document_package_number = '%s'" % exp_values[len(exp_values) - 1])[0][0]) # Статус
                        db_value.append(db.query("SELECT n.name FROM npa n left join document_package dp on n.document_package_id=dp.id where dp.document_package_number = '%s'" % exp_values[len(exp_values) - 1])[0][0]) # Наименование
                if 'review-date' in sc[x]:
                    with ps.open('pq://npa:npa@172.17.21.166:5432/npa') as db:
                        db_value.append(db.query("SELECT (rd.planned_review_date)::date FROM review_date rd LEFT join document_package dp on rd.document_package_id = dp.id WHERE dp.document_package_number ='%s'" % exp_values[len(exp_values) - 1])[0][0]) # Плановая дата рассмотрения
                        db_value.append(db.query("SELECT rd.approval_form_id FROM review_date rd LEFT join document_package dp on rd.document_package_id = dp.id WHERE dp.document_package_number ='%s'" % exp_values[len(exp_values) - 1])[0][0]) # Формат утверждения
                        db_value.append(db.query("SELECT (rd.reason_date_review) FROM review_date rd LEFT join document_package dp on rd.document_package_id = dp.id WHERE dp.document_package_number ='%s'" % exp_values[len(exp_values) - 1])[0][0]) # Обоснование даты рассмотрения
                        if db_value[5] is not 'Null':
                            stack_result.append(1)
                        else:
                            stack_errors.append('Планируемая дата рассмотрения - не ОК: ' + str(db_value[5]))
                    
                        if db_value[6] == exp_values[4]:
                            stack_result.append(1)
                        else:
                            stack_errors.append('Формат утверждения - не ОК: ' + str(db_value[6]))
                    
                        if db_value[7] == exp_values[5]:
                            stack_result.append(1)
                        else:
                            stack_errors.append('Обоснование - не ОК: ' + str(db_value[7]))
                        
                print('Ожидаемые значения' + str(exp_values))
                print(db_value)
                if db_value[0] == 1:
                    stack_result.append(1)
                    print('Найден 1 пакет документа')
                else:
                    stack_errors.append('Найдено кол-во пакетов ' + str(db_value[0]))
                if str(db_value[1]) == exp_values[0]:
                    
                    stack_result.append(1)
                else:
                    print(db_value[1], exp_values[0])
                    stack_errors.append('Сохраненное значение типа пакета в БД не ОК: ' + str(db_value[1]))

                if db_value[2] == exp_values[1]:
                    stack_result.append(1)
                else:
                    stack_errors.append('Тип проекта сохранился в БД не ОК ' + str(db_value[2]))

                if db_value[3] == exp_values[2]:
                    stack_result.append(1)
                else:
                    stack_errors.append('Статус - не ОК ' + str(db_value[3]))

                if db_value[4] == exp_values[3]:
                        stack_result.append(1)
                else:
                    stack_errors.append('Наименование - не ОК: ' + str(db_value[4]))
               

    
    if stack_errors == []:
        print('Все тесты пройдены')
    else:
        print(stack_errors)



# Запускаем тестовый сценарий
driver = wd.Chrome(chrome_options=chrome_options)
# result = executer()
# print(result)
# if result != None:
#     db_check(result)

negative(scenario_3)