import requests as r
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from collections import Counter
import csv

import sys
import codecs

try:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
except:
    pass


def getValidCodes(c_code="E01244"):
    link = f"https://irbank.net/{c_code}/reports"
    rs = r.get(link)
    rsp = BeautifulSoup(rs.content, "html.parser")

    table = rsp.find("table")
    stock_slice_batch = pd.read_html(str(table), extract_links="all")[0]
    list_block = table.find_all("td")
    dict_ = {}
    for block in list_block:
        list_a = block.find_all("a")
        try:
            link_basic = list_a[0]["href"]
            link = list_a[-1]["href"]
            key = f"{link_basic}"
            dict_[key] = link
        except:
            pass

    for col in stock_slice_batch.columns[0:5]:
        for row in stock_slice_batch.index:
            t = stock_slice_batch[col][row]
            for key in dict_.keys():
                if t[1] == key:
                    stock_slice_batch[col][row] = dict_[key]

    fy_report_codes = stock_slice_batch[("通期", None)]
    fy_old_report_codes = stock_slice_batch[("年度", None)]

    result = []
    for code in fy_report_codes:
        if code[-2:] == "pl" and code[:-3] not in result:
            result.append(code[:-3])

    for code in fy_old_report_codes:
        if code[-2:] == "pl" and code[:-3] not in result:
            result.append(code[:-3])

    return result

def normalize_series(series, delimiter="__"):
    suffix_counts = Counter([v.split(delimiter)[-1] for v in series])
    for i in range(len(series)):
        suff = series[i].split(delimiter)[-1]
        if suffix_counts[suff] == 1:
            series[i] = suff
    return series


def get_data(table, useAllColumns = False):
    data = []
    
    rows = table.find_elements(By.XPATH, ".//tbody/tr")

    headers = rows[0].find_elements(By.XPATH, ".//th")
    header_range = range(len(headers)) if (len(headers)<=2 or useAllColumns) else range(0, len(headers), 2)
    h = [headers[i].text.replace("\n", " ") for i in header_range]
    data.append(h)

    indents = [[] for i in range(10)]
    for row in rows[1:]:
        r = []
        cols = row.find_elements(By.XPATH, ".//td")
        for col in cols:
            class_of_col = col.get_attribute("class").split(" ")[0]
            if "indent" in class_of_col:
                try:
                    number = int(class_of_col[-1])
                except:
                    number = 0
                    print(f"Something wrong with this indent: {class_of_col}")
                indents[number].append(col.text.replace("\n", " "))
                txt = indents[number][-1]
                number -= 1
                while number > 0:
                    if len(indents[number]) > 0:
                        txt = indents[number][-1] + "__" + txt
                    number -= 1
                r.append(txt)
            else:
                if cols[-1] == col or useAllColumns:
                    r.append(col.text.replace("\n", " "))
        data.append(r)
    data = pd.DataFrame(data)
    data.iloc[:, 0] = normalize_series(data.iloc[:, 0])

    if len(data.columns) > 2:
        first_column = data.columns[0]
        extracted_dfs = [data[[first_column, column]] for column in data.columns[1:]]
    else:
        extracted_dfs = [data]
    return extracted_dfs[::-1]

def concat_data(dfs):
    v_index_val = []
    for df in dfs:
        for v in df.iloc[:, 0]:
            if v not in v_index_val:
                v_index_val.append(v)

    dict_data = {k: [] for k in v_index_val}

    for df in dfs:
        for k in v_index_val:
            index_column = df.iloc[:, 0]
            if k in index_column.tolist():
                idx = index_column[index_column == k].index[0]
                dict_data[k].append(df.iloc[idx, -1])
            else:
                dict_data[k].append("")

    return dict_data

def writeToCsv(data, path):
    with open(
        path,
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows([[k] + v for k, v in data.items()])