from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import ElementNotVisibleException as NotVisible
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import csv
import pandas as pd


NUM_RECIPE_LINKS = 15000

'''
*Mon khai vi (3547 recipes): https://www.cooky.vn/cach-lam/mon-khai-vi-c1?st=7
*Mon chay (1505 recipes): https://www.cooky.vn/cach-lam/mon-chay-c3?st=7
*Mon trang mieng (4902 recipes): https://www.cooky.vn/cach-lam/mon-trang-mieng-c2?st=7
*Mon an sang (4045 recipes): https://www.cooky.vn/cach-lam/mon-an-sang-c5?st=7
*Thuc uong (2131 recipes): https://www.cooky.vn/cach-lam/thuc-uong-c7?st=7
*Banh ngot (4884 recipes): https://www.cooky.vn/cach-lam/banh-banh-ngot-c8?st=7
*Mon cho be (296 recipes): https://www.cooky.vn/cach-lam/mon-an-cho-tre-c9?st=7
*Mon chinh (13793 recipes): https://www.cooky.vn/cach-lam/mon-chinh-c4?st=7
'''

# Connect
options = Options()
options.headless = True
options.add_argument('--window-size=1920,1200')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# Get links first time load page
driver = webdriver.Chrome(options=options, service=Service('./chromedriver.exe'))
driver.get("https://www.cooky.vn/cach-lam/mon-chinh-c4?st=7")
time.sleep(1)

links = driver.find_elements(
    By.XPATH, "//div[@class='result-recipe-item ng-scope']//a[@rel='aslternate'][@class='ng-binding']")

# Load more and save to csv
while len(links) < NUM_RECIPE_LINKS:
    print(len(links))
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a[href='javascript:void(0)'][ng-click='loadMore()']"))).click()
    except NotVisible:
        pass
    time.sleep(1)
    links = driver.find_elements(
        By.XPATH, "//div[@class='result-recipe-item ng-scope']//a[@rel='alternate'][@class='ng-binding']")
    if len(links) % 13788 == 0:
        links_list = []
        for link in links:
            links_list.append(link.get_attribute('href'))
        df = pd.DataFrame(links_list)
        df.to_csv('mon-chinh.csv')
        print("Save {} links to csv file!".format(len(links)))
        break
driver.quit()
