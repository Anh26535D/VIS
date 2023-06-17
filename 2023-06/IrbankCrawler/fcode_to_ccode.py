import csv
import pandas as pd
from IrbankCrawler import IrbankCrawler

LIST_COMPANIES_PATH = "G:/My Drive/IrbankCrawler/List_company_23052023.xlsx"

companyIDs = pd.read_excel(LIST_COMPANIES_PATH, sheet_name='Delisting_before_2014')
crawler = IrbankCrawler()

data = []
title = ["fcode", "ccode"]
data.append(title)

for f_code in companyIDs['Symbol']:
    f_code = int(f_code)
    res = crawler.getCompanyCode(f_code)
    data.append(res)

# Write data to CSV file
with open('delist_before_ccode.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(data)
