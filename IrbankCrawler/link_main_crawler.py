import pandas as pd
import re
import requests
from CommonLink import CommonLink
from bs4 import BeautifulSoup
import os

import sys
import codecs

try:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
except:
    pass

from selenium import webdriver
from selenium.webdriver.common.by import By

SAVE_PATH = "E:/vis/vis_repo/2023-06/IrbankCrawler/Link_financial"
codes = pd.read_csv("missing_company.csv")

options = webdriver.edge.options.Options()
options.add_argument("--headless")
options.add_argument("enable-automation")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-extensions")
options.add_argument("--dns-prefetch-disable")
options.add_argument("--disable-gpu")

def setReportLink(code):
    link = CommonLink.REPORT_LINK
    link = link.replace("financial_code", str(code))
    return link

def formatData(value):
    date_pattern = r"\d{4}/\d{2}"
    sublink_pattern = r"@@(\d.+/pl)"
    extracted_date = ""
    extracted_sublink = ""
    date_match = re.search(date_pattern, value)
    sublink_match = re.search(sublink_pattern, value)
    if date_match:
        extracted_date = date_match.group()
    if sublink_match:
        extracted_sublink = sublink_match.group(1)
    return ",".join([extracted_date, extracted_sublink])

def formatTableData(table_data):
    for idx in table_data.index:
        for col in table_data.columns:
            table_data.loc[idx, col] = formatData(table_data.loc[idx, col])
    table_data.index = table_data.index.map(formatData)
    return table_data

def setReportLink(code):
    link = CommonLink.REPORT_LINK
    link = link.replace("financial_code", str(code))
    return link

def formatData(value):
    date_pattern = r"\d{4}/\d{2}"
    sublink_pattern = r"@@(\d.+/pl)"
    extracted_date = ""
    extracted_sublink = ""
    date_match = re.search(date_pattern, value)
    sublink_match = re.search(sublink_pattern, value)
    if date_match:
        extracted_date = date_match.group()
    if sublink_match:
        extracted_sublink = sublink_match.group(1)
    return ",".join([extracted_date, extracted_sublink])

def formatTableData(table_data):
    for idx in table_data.index:
        for col in table_data.columns:
            table_data.loc[idx, col] = formatData(table_data.loc[idx, col])
    table_data.index = table_data.index.map(formatData)
    return table_data

def getTableOfLinks(ccode, year_col="年度", drop_cols=["修正等"], delimiter="@@"):
    link = setReportLink(ccode)
    rs = requests.get(link)
    
    rsp = BeautifulSoup(rs.content, "html.parser")
    table = rsp.find("table")

    header_rows = table.find("thead").find_all("tr")
    header_data = [cell.get_text() for row in header_rows for cell in row.find_all("th")]

    body_rows = table.find("tbody").find_all("tr")
    body_data = [
        [
            cell.get_text() + delimiter + a_tags[-1]["href"] if a_tags else cell.get_text()
            for cell in row.find_all("td")
            for a_tags in [cell.find_all("a")]
        ]
        for row in body_rows
    ]

    table_data = pd.DataFrame(body_data, columns=header_data).set_index(year_col)
    drop_cols = [col for col in drop_cols if col in table_data.columns]
    table_data = table_data.drop(drop_cols, axis=1)
    try:
        null_row_index = table_data.index[table_data.isnull().all(axis=1)].to_list()
        if len(null_row_index) == 1:
            table_data_above_null = table_data.iloc[:table_data.index.get_loc(null_row_index[0])]
            table_data_below_null = table_data.iloc[table_data.index.get_loc(null_row_index[0])+1:]
            table_data_above_null = formatTableData(table_data_above_null)
            table_data_below_null = formatTableData(table_data_below_null)
            
            column_names = table_data_below_null.columns.tolist()
            index_name = table_data_below_null.index.name
            table_data_below_null = table_data_below_null.reset_index()

            prev_years = []
            link = []
            for i in range(table_data_below_null.shape[0]):
                for j in range(table_data_below_null.shape[1]):
                    if len(table_data_below_null.iloc[i, j]) > 4:
                        prev_years.append(table_data_below_null.iloc[i, j].split(",")[0])
                        link.append(table_data_below_null.iloc[i, j].split(",")[1])
            
            returned_df = pd.DataFrame(index=prev_years, columns=column_names)
            returned_df.index.name = index_name
            for i in range(returned_df.shape[0]):
                returned_df.iloc[i, -1] = link[i]
                    
            table_data = pd.concat([table_data_above_null, returned_df], axis=0)
        else:
            table_data = formatTableData(table_data)
    except Exception as e:
        raise Exception(f"Something's wrong with {ccode}! See standard format table in https://irbank.net/E02865/reports") from e
    
    table_data.index = table_data.index.str.replace(",", "")
    table_data = table_data.applymap(lambda x: str(x).replace(",", "") if "pl" in str(x) else "")
    return table_data

def getPrevLinks(root_link):
    results = []
    prev_link = ""
    driver.get(root_link)
    try:
        prev_link = (driver.find_element(By.XPATH, '//*[@id="c_pl1"]/caption/ul/li[1]/a')\
                            .get_attribute("href"))
        if prev_link == root_link:
            return results
        results.append(prev_link)
        while(prev_link):
            driver.get(prev_link)
            prev_link = (driver.find_element(By.XPATH, '//*[@id="c_pl1"]/caption/ul/li[1]/a')\
                            .get_attribute("href"))
            if prev_link == results[-1]:
                break
            results.append(prev_link) 
    except:
        pass
    return results

crawled_symbols = os.listdir(SAVE_PATH)
for f_code, code in codes[["fcode", "ccode"]].to_numpy():
    if str(code) + ".csv" not in crawled_symbols:
        print(f"Start with {f_code} - {code}")
        table = f"https://irbank.net/{code}/" + getTableOfLinks(code)

        table = pd.DataFrame(table["通期"])

        MAX_TRIAL = 100
        try:
            for trial in range(MAX_TRIAL):
                driver = webdriver.Edge(options=options)
                driver.set_page_load_timeout(60)
                for col in table.columns:
                    financial_report = table[col]
                    i = 0
                    while i < len(financial_report):
                        print(i, end=" ")
                        root_link = financial_report[i]
                        prev_links = getPrevLinks(root_link)
                        if prev_links:
                            financial_report[i+1:i+1+len(prev_links)] = prev_links
                            i += len(prev_links)
                        else:
                            i += 1
                    table[col] = financial_report
                driver.quit()
                break
        except:
            pass

        table.to_csv(f"{SAVE_PATH}/{code}.csv")