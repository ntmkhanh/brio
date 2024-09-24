from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import os
import time
import csv
import pandas as pd
import glob


def connect():
    options = Options()
    options.headless = True
    options.add_argument('--window-size=1920,1200')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(
        options=options, service=Service('./chromedriver.exe'))
    return driver


def scrape_recipe_link(r, driver):
    driver.get(r['Link'])
    # driver.implicitly_wait(10)

    ''' Scrapers:
    title, type, servings, ingredients, quantity, instructions
    '''
    link = r['Link']
    # Title
    global title, servings, ingredients, quantity, instruction
    try:
        title = driver.find_element(By.CLASS_NAME, "active").text
    except NoSuchElementException:
        print("Exception Title handled")
        pass

    # Servings
    try:
        servings = driver.find_element(
            By.XPATH, "//*[@id='app']/div[8]/div/div/div[1]/div[3]/div[5]/span").text.lstrip("Khẩu phần: ")
    except NoSuchElementException:
        print("Exception Servings handled")
        pass

    # Ingredients
    try:
        ingredients = driver.find_elements(By.CLASS_NAME, "ingredient-name")
        ingredients_ls = []
        for i in ingredients:
            ingredients_ls.append(i.text)
    except NoSuchElementException:
        print("Exception Ingredients handled")
        pass

    # Quantity
    try:
        quantity = driver.find_elements(By.CLASS_NAME, "ingredient-item")
        quantity_ls = []
        for q in quantity:
            quantity_ls.append(q.text.replace("\n", ": "))
    except NoSuchElementException:
        print("Exception Quantity handled")
        pass

    # Instruction
    try:
        instruction = driver.find_elements(By.CLASS_NAME, "step-content")
        instruction_ls = []
        for ins in instruction:
            instruction_ls.append(ins.text)
    except NoSuchElementException:
        print("Exception Instruction handled")
        pass

    recipe_dict = {'Title': title, 'Servings': servings, 'Ingredients': ingredients_ls,
                   'Quantity': quantity_ls, 'Instructions': instruction_ls, 'Link': link}
    return recipe_dict


if __name__ == '__main__':

    driver = connect()
    listfile = glob.glob(os.path.join('./raw_datalink', '*.csv'))
    time.sleep(5)
    for l in listfile:

        links = pd.read_csv(l, index_col=0)
        temp_list = []
        file_name = l.lstrip("./raw_datalink/")
        start_time = time.time()  # Check time
        print("Scraping {} file:".format(l))

        for idx, row in links.iterrows():
            recipe_dict = scrape_recipe_link(row, driver)
            temp_list.append(recipe_dict)
            if idx % 10 == 0:
                print("Current: {} links. Saving recipes...".format(idx))
                df = pd.DataFrame(temp_list)
                df.to_csv('CookyVN_{}'.format(file_name))
            print("Scraped {}".format(idx))

        df = pd.DataFrame(temp_list)
        df.to_csv('CookyVN_{}'.format(file_name))
        print("{} done!".format(file_name))
        print("Columns: {}".format(list(df.columns.values.tolist())))
        print("Total links scraped: {}".format(len(temp_list)))
        print("Time: %.5s (s)" % (time.time() - start_time))
    driver.close()
