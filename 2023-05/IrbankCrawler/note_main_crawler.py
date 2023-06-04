from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import chrome
from selenium.webdriver import edge
from selenium.webdriver.chrome.service import Service
from time import sleep
import csv
from tqdm import tqdm
import gc
from IrCrawlHelper import *

ROOT_PATH = "G:/My Drive/IrbankCrawler"
LIST_COMPANIES_PATH = "G:/My Drive/IrbankCrawler/full_ccode.csv"
EXECUTABLE_PATH = "C:/web_driver/chromedriver.exe"
BROWSER = "edge"

if BROWSER == "chrome":
    service = Service(EXECUTABLE_PATH)
    options = chrome.options.Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=service, options=options)
else:
    options = edge.options.Options()
    options.add_argument("--headless=new")
    driver = webdriver.Edge(options=options)    

ROOT_LINK = "https://irbank.net/"

companyIDs = pd.read_csv(LIST_COMPANIES_PATH)

for f_code, C_CODE in companyIDs[["fcode", "ccode"]].to_numpy():
    print(f"====== BEGIN {f_code}: {C_CODE} ======")
    # Clear old driver
    del driver
    _ = gc.collect()
    if BROWSER == "chorme":
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Edge(options=options)

    data = []
    title = ["Note", "Name", "Content"]
    data.append(title)
    
    link = ROOT_LINK + f"{C_CODE}/dividend"
    driver.get(link)

    elements = driver.find_elements(By.CSS_SELECTOR, "[id^='note_']")
    for element in elements:
        row = []
        try:
            sup = element.find_element(By.TAG_NAME, "sup").text
        except:
            sup = element.get_attribute("id").split("_")[-1]
        row.append(sup)
        row.append(element.text.replace(sup, '', 1))
        try:
            content = element.find_element(By.XPATH, "following-sibling::dd")
            row.append(content.text)
        except:
            row.append("")
            print(f"Somthing wrong with content of {C_CODE}")
        data.append(row)
    with open(
        ROOT_PATH + f"/Note/{f_code}.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data)

    print(f"====== END {f_code}======")