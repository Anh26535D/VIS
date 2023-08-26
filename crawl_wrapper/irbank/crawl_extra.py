import pandas as pd
import os
import tqdm
import pandas as pd
from selenium.webdriver.common.by import By
from collections import Counter, defaultdict
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver import edge


IGNORE_FLAG = False
# IGNORE_FLAG controls whether existing files should be re-crawled.
# Set IGNORE_FLAG to True if you wish to skip crawling already processed files.

ROOT_PATH = r"E:\vis\vis_repo\2023-08\IrbankCrawler"

PL_SAVE_DIR = os.path.join(ROOT_PATH, "Financial_extra", "IncomeStatement")
BS_SAVE_DIR = os.path.join(ROOT_PATH, "Financial_extra", "BalanceSheet")

LINKS_DIR = os.path.join(ROOT_PATH, "Financial_extra", "links")

LIST_COMPANIES_PATH = os.path.join(ROOT_PATH, "test.csv")

def normalizeSeries(series, delimiter="__"):
    suffix_counts = Counter([v.split(delimiter)[-1] for v in series])
    for i in range(len(series)):
        suff = series[i].split(delimiter)[-1]
        if suffix_counts[suff] == 1:
            series[i] = suff

    count_dict = {}
    new_list = []

    for item in series:
        if item in count_dict:
            count_dict[item] += 1
            new_list.append(f"{item}__{count_dict[item]}")
        else:
            count_dict[item] = 1
            new_list.append(item)
    return new_list

def getDataFromTable(table, useAllColumns=True):

    data = []
    
    rows = table.find_elements(By.XPATH, ".//tbody/tr")

    headers = rows[0].find_elements(By.XPATH, ".//th")
    header_range = range(len(headers)) if (len(headers)<=2 or useAllColumns) else range(0, len(headers), 2)
    h = [headers[i].text.replace("\n", " ") for i in header_range]
    data.append(h)
    currency_unit = table.find_element(By.XPATH, ".//caption/span").text.strip()
    if len(header_range) > 1:
        data.append(["Currency"] + [currency_unit for i in range(len(header_range)-1)])
    else:
        data.append(["Currency"])
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
    columns = data[0]
    data = data[1:]
    data = pd.DataFrame(data, columns=columns)
    data.iloc[:, 0] = normalizeSeries(data.iloc[:, 0])

    if len(data.columns) > 2:
        first_column = data.columns[0]
        extracted_dfs = [data[[first_column, column]] for column in data.columns[1:]]
    else:
        extracted_dfs = [data]
    return extracted_dfs[::-1]

def concatData(list_df):
    result_df = list_df[0]
    on_key = result_df.columns[0]
    # Merge the subsequent DataFrames on the 'Title' column one by one
    for i in range(1, len(list_df)):
        result_df = result_df.merge(list_df[i], on=on_key, how='outer')

    return result_df

def getData(company_code, report_type="pl"):
    options = edge.options.Options()
    options.add_argument("--headless=new")
    driver = webdriver.Edge(options=options)
       
    if report_type not in ("pl", "bs"):
        raise "Only valid with Income Statent or Balance Sheet type"
    
    dfs = defaultdict()

    document_codes = pd.read_csv(os.path.join(LINKS_DIR, f"{company_code}.csv"))["通期"].to_list()
    for i, document_code in tqdm(enumerate(document_codes)):
        print(i, document_code)
        if "pl" not in document_code:
            continue
        link = document_code.replace("pl", str(report_type))
        
        if report_type not in ("pl", "bs"):
            raise "Only valid with Income Statent or Balance Sheet type"
    
        dt_tables = []
        report_type = link[-2:]
        try:
            driver.get(link)
            table = driver.find_element(By.ID, f"c_{report_type}1")
        except:
            print(f"============ {link} has no {report_type} data or something wrong with provided link")
            continue
        dt_tables = getDataFromTable(table, True)
        
        for dt_table in dt_tables:
            key_table = dt_table.columns.to_list()[1].strip()
            if key_table not in dfs.keys():
                dfs[key_table] = dt_table
    try:
        data = concatData([v[1] for v in dfs.items()])
    except:
        data = pd.DataFrame()
        
    driver.close()
    return data

companyIDs = pd.read_csv(LIST_COMPANIES_PATH)

crawled_pl_symbols = os.listdir(PL_SAVE_DIR)
crawled_bs_symbols = os.listdir(BS_SAVE_DIR)

for symbol, code in companyIDs[["Symbol", "Code"]].to_numpy():
    print(f"====== BEGIN {symbol}: {code} ======")
    for REPORT_TYPE in ["pl", "bs"]:
        if (IGNORE_FLAG):
            if ((REPORT_TYPE == "pl") and (f"{symbol}.csv" in crawled_pl_symbols)):
                continue
            if ((REPORT_TYPE == "bs") and (f"{symbol}.csv" in crawled_bs_symbols)):
                continue

        print(f"============ begin type: {REPORT_TYPE}")
        
        data = getData(code, report_type=REPORT_TYPE)
        if REPORT_TYPE == "pl":
            save_path = os.path.join(PL_SAVE_DIR, f"{symbol}.csv")
        elif REPORT_TYPE == "bs":
            save_path = os.path.join(BS_SAVE_DIR, f"{symbol}.csv")
        
        data.to_csv(save_path, index=False)

    print(f"====== END {symbol}======")
