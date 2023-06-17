from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import chrome
from selenium.webdriver.chrome.service import Service
import csv
from tqdm import tqdm
import gc
import pandas as pd

ROOT_PATH = "F:/DVA_irbank"
LIST_COMPANIES_PATH = "F:/DVA_irbank/full_ccode.csv"
EXECUTABLE_PATH = "C:/web_driver/chromedriver.exe"


service = Service(EXECUTABLE_PATH)
options = chrome.options.Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--start-maximized")
options.add_argument("enable-automation")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-browser-side-navigation")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(service=service, options=options)

ROOT_LINK = "https://irbank.net/"

companyIDs = pd.read_csv(LIST_COMPANIES_PATH)

TIMER = 20

for f_code, C_CODE in companyIDs[["fcode", "ccode"]].to_numpy():
    print(f"====== BEGIN {f_code}: {C_CODE} ======")
    # Clear old driver
    if TIMER <= 0:
        TIMER = 20
        del driver
        _ = gc.collect()
        driver = webdriver.Chrome(service=service, options=options)
    else:
        TIMER -= 1

    data = []
    title = ["Note", "Name", "Content"]
    data.append(title)

    link = ROOT_LINK + f"{C_CODE}/dividend"
    driver.get(link)

    elements = driver.find_elements(By.CSS_SELECTOR, "[id^='note_']")
    for element in tqdm(elements):
        row = []
        try:
            sup = element.find_element(By.TAG_NAME, "sup").text
        except:
            sup = element.get_attribute("id").split("_")[-1]
        row.append(sup)
        row.append(element.text.replace(sup, "", 1))
        try:
            content = element.find_element(By.XPATH, "following-sibling::dd")
            row.append(content.text)
        except:
            row.append("")
            print(f"Something wrong with content of {C_CODE}")
        data.append(row)
    with open(
        ROOT_PATH + f"/DividendNote/{f_code}.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data)

    print(f"====== END {f_code}======")
