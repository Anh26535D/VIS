from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import edge
from time import sleep
import csv
from IrCrawlHelper import *

options = edge.options.Options()
options.add_argument("--headless=new")
driver = webdriver.Edge(options=options)

REPORT_TYPE = "bs"
C_CODE = "E01244"

codes = getValidCodes(C_CODE)

dfs = []

for code in codes:
    link = f"https://irbank.net/{C_CODE}/{code}/{REPORT_TYPE}"
    print(link)
    driver.get(link)
    sleep(1)

    table = driver.find_element(By.ID, f"c_{REPORT_TYPE}1")
    data = get_data(table)
    dfs.append(data)
print("DONE!!!")
data = concat_data(dfs)
driver.quit()

with open(f'data_{C_CODE}_{REPORT_TYPE}.csv', 'w', newline='', encoding='utf-8') as csvfile: 
    csvwriter = csv.writer(csvfile)  
    csvwriter.writerows([[k] + v for k, v in data.items()])