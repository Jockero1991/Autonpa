import postgresql as ps
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")
caps=DesiredCapabilities.CHROME
caps['loggingPrefs']={'browser': 'ALL'}

# ввести текст по переданному селектору

# раскрыть выпадающий список, выбрать значение

# нажать кнопку по переданному селектору

# ввести текст и выбрать значение

# Получить текст элемента по переданному селектору
