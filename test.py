import requests
from bs4 import BeautifulSoup
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from selenium import webdriver  
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import os.path


def Main():

    """Shows Peujeot 3008 info"""
    market_filter = "https://999.md/ru/list/transport/cars?hide_duplicates=no&applied=1&show_all_checked_childrens=no&ef-=260,1,6,5,4,1279,4112,2029&eo=76,860&o_1_2095_76_860=36726,36727&aof=1&r_6_2_from=&r_6_2_to=&r_6_2_unit=eur&r_6_2_negotiable=yes&o_4_151=161,22987"
    # market_filter = "https://999.md/ru/list/transport/cars?hide_duplicates=no&applied=1&show_all_checked_childrens=no&ef=260,1,6,5,4,1279,4112,2029&eo=76,860&o_1_2095_76_860=36726,36727&aof=1&r_6_2_from=&r_6_2_to=&r_6_2_unit=eur&r_6_2_negotiable=yes"
    # r = requests.get(market_filter, stream=True)
    # content = r.text.encode('utf-8')

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    browser = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
    browser.get(market_filter)
    WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, "div[data-sentry-component='AdList'] div[class*='AdPhoto_wrapper']")))

    html = browser.page_source
    soup = BeautifulSoup(html, features="lxml")
    browser.quit()


    old_list = []
    new_list = []
    diff = []


    if os.path.isfile("old_res.json"):
        with open('old_res.json', encoding="utf-8") as f:
            old_list = json.load(f)


    car_list = soup.select("div[data-sentry-component='AdList']")
    print(car_list)
    for car in car_list:
        car_object = {}
        car_object['link'] = "https://999.md" + car.select_one("a[data-test-id*='item-title']").get('href').replace(" ", "")
        title_text = car.select_one("a[data-test-id*='item-title']").text.replace(" ", "")
        car_object['title'], car_object['year'] = title_text.split(",")
        car_object['year'] = car_object['year'].replace(".", "")
        car_object['price'] = car.select_one("span[class*='AdPrice_price']").text.replace("\xa0", "").replace(" ", "")
        probeg = car.select_one("span[class*='AdPrice_info']").text.replace(" ", "")
        if ":" not in probeg: 
            car_object['km'] = probeg 
        else:
            car_object['km'] = "-"

        if "clickToken" not in car_object['link']:
            new_list.append(car_object)

    for item in new_list:
        if item not in old_list:
            diff.append(item)
        elif old_list == []:
            diff.append(item)


    if not diff:
        print("No new items found")
    else:
        with open('old_res.json', 'w', encoding="utf-8") as f:
            f.write(json.dumps(new_list, indent=4, ensure_ascii=False))

    print(f"Количество объявлений: {len(new_list)}\nНовых:{len(diff)}\nНовые:\n{'\n'.join(map(str,diff))}")

Main()