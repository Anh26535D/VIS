from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import chrome
from selenium.webdriver.chrome.service import Service
from time import sleep
import csv
from tqdm import tqdm
import gc
from IrCrawlHelper import *

ROOT_PATH = "F:/DVA_irbank"
LIST_COMPANIES_PATH = "F:/DVA_irbank/ccode.csv"
EXECUTABLE_PATH = "C:/web_driver/chromedriver.exe"


service = Service(EXECUTABLE_PATH)
options = chrome.options.Options()
options.add_argument("--headless=new")

ROOT_LINK = "https://irbank.net/"

companyIDs = pd.read_csv(LIST_COMPANIES_PATH)

# driver = webdriver.Chrome(options=options)

for f_code, C_CODE in companyIDs[["fcode", "ccode"]][2678:].to_numpy():
    print(f"====== BEGIN {f_code}: {C_CODE} ======")

    for REPORT_TYPE in ["pl", "bs"]:
        print(f"============ begin type: {REPORT_TYPE}")
        dfs = []
        data = {}

        try:
            codes = getValidCodes(
                C_CODE
            )  # if the company has no data, it will raise an exception
        except:
            print(f"============ {f_code} has no {REPORT_TYPE} data")
            continue

        driver = webdriver.Chrome(options=options)
        length_codes = len(codes)
        for i in tqdm(range(length_codes)):
            link = f"https://irbank.net/{C_CODE}/{codes[i]}/{REPORT_TYPE}"
            try:  # if the code has no data, it will raise an exception
                driver.get(link)
                sleep(1)

                table = driver.find_element(By.ID, f"c_{REPORT_TYPE}1")
            except:
                print(f"============ {codes[i]} has no {REPORT_TYPE} data")
                continue
            if i == length_codes - 1:
                dt_tables = get_data(table, True)
            else:
                dt_tables = get_data(table)
            for dt_table in dt_tables:
                dfs.append(dt_table)
        data = concat_data(dfs)

        # # Clear old driver
        # del driver
        # _ = gc.collect()
        driver.close()

        if REPORT_TYPE == "pl":
            report_comp = "IncomeStatement"
        elif REPORT_TYPE == "bs":
            report_comp = "BalanceSheet"
        with open(
            ROOT_PATH + f"/Financial_2/{report_comp}/{f_code}.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows([[k] + v for k, v in data.items()])
    print(f"====== END {f_code}======")
