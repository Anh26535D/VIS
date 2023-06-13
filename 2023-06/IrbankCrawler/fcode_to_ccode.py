import requests
import csv
from time import sleep
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

LIST_COMPANIES_PATH = "G:/My Drive/IrbankCrawler/List_company_23052023.xlsx"
ROOT_LINK = "https://irbank.net/"

companyIDs = pd.read_excel(LIST_COMPANIES_PATH, sheet_name='Delisting_before_2014')
data = []
title = ["fcode", "ccode"]
data.append(title)

session = requests.Session()

def process_f_code(f_code):
    link = ROOT_LINK + str(f_code) + "/reports"
    try:
        response = session.get(link)
        if response.status_code == 200:
            report_url = response.url
            c_code = report_url.split("/")[3]
            data.append([f_code, c_code])
            print(f"{f_code} : {c_code}")
        else:
            print(f"Something wrong with {f_code}")
    except requests.exceptions.RequestException:
        pass

# Use multithreading to send requests concurrently
with ThreadPoolExecutor(max_workers=10) as executor:
    for f_code in companyIDs['Symbol']:
        try:
            f_code = int(f_code)
            executor.submit(process_f_code, f_code)
            sleep(1)
        except:
            pass

# Write data to CSV file
with open('delist_before_ccode.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(data)
