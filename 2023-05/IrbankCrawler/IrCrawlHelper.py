import requests as r
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

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

    for col in stock_slice_batch.columns[1:5]:
        for row in stock_slice_batch.index:
            t = stock_slice_batch[col][row]
            for key in dict_.keys():
                if t[1] == key:
                    stock_slice_batch[col][row] = dict_[key]

    fy_report_codes = stock_slice_batch[("通期", None)]
    result = []
    for code in fy_report_codes:
        if code[-2:] == "pl" and code[:-3] not in result:
            result.append(code[:-3])

    return result


def normalize_series(series, delimiter="__"):
    suffix = []
    for v in series:
        lst = v.split(delimiter)
        suffix.append(lst[-1])
    for i in range(len(series)):
        suff = series[i].split(delimiter)[-1]
        if suffix.count(suff) == 1:
            series[i] = suff
    return series


def get_data(table):
    data = []
    h = []
    rows = table.find_elements(By.XPATH, ".//tbody/tr")
    headers = rows[0].find_elements(By.XPATH, ".//th")
    if len(headers) > 2:
        for header in headers[0::2]:
            value = header.text.replace("\n", " ")
            h.append(value)
    else:
        for header in headers:
            value = header.text.replace("\n", " ")
            h.append(value)
    data.append(h)

    mem = []
    prev_check = 0
    for row in rows[1:]:
        r = []
        cols = row.find_elements(By.XPATH, ".//td")
        cls = row.get_attribute("class")
        if cls == "row3":
            if prev_check == 1:
                mem[-1] = mem[-1] + "___" + cols[0].text.replace("\n", " ")
            else:
                mem.append(cols[0].text.replace("\n", " "))
            prev_check = 1
        else:
            prev_check = 0
            value = cols[0].text.replace("\n", " ")
            if len(mem) > 0:
                value = str(mem[-1]) + "__" + value
            r.append(value)

            value = cols[-1].text.replace("\n", " ")
            r.append(value)
            data.append(r)

    return pd.DataFrame(data)


def concat_data(dfs):
    v_index_val = []
    h_index_val = []
    for df in dfs:
        for v in df.iloc[:, 0]:
            if v not in v_index_val:
                v_index_val.append("{}".format(v))
        for v in df.loc[0]:
            if v not in h_index_val:
                h_index_val.append("{}".format(v))
    h_index_val = h_index_val[1:]
    dict_data = {k: [] for k in v_index_val}
    for df in dfs:
        for k in dict_data.keys():
            temp_df = df.iloc[:, 0]
            if k in temp_df.tolist():
                idx = 0
                for value in temp_df:
                    if value == k:
                        break
                    idx += 1
                dict_data[k].append(df.iloc[idx, -1])
            else:
                dict_data[k].append("")

    old_keys = [format(v) for v in dict_data.keys()]
    new_keys = normalize_series(old_keys)
    dataset = {}
    old_keys = [format(v) for v in dict_data.keys()]
    for old_key, new_key in zip(old_keys, new_keys):
        dataset[new_key] = dict_data[old_key]
    return dataset
