from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import ElementNotVisibleException as NotVisible
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys

def connect():
  options = Options()
  options.headless = True
  options.add_experimental_option('excludeSwitches', ['enable-logging'])
  serv = Service("C://Users//phamt//Desktop//LVTN//flask-project//back-end//etc//chromedriver.exe")
  driver = webdriver.Chrome(service=serv,options=options)
  return driver

def get_image_url(title):
    driver = connect()
    # Google Images
    query = title
    # Open Google Images in the browser
    driver.get('https://images.google.com/')
    # Finding the search box
    box = driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input')
    # Type the search query in the search box
    box.send_keys(query)
    # Pressing enter
    box.send_keys(Keys.ENTER)
    element = driver.find_element(By.XPATH,'//div/div/a/div/img')
    image_url = element.get_attribute('src')
    driver.close()
    return image_url