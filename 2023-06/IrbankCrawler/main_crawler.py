import csv
from IrbankCrawler import IrbankCrawler
import pandas as pd

ROOT_PATH = "E:/vis/vis_repo/2023-06/IrbankCrawler"
LIST_COMPANIES_PATH = ROOT_PATH + "/" + "codes.csv"

companyIDs = pd.read_csv(LIST_COMPANIES_PATH)

crawler = IrbankCrawler(browser="edge")

for f_code, C_CODE in companyIDs[["fcode", "ccode"]].to_numpy():
    print(f"====== BEGIN {f_code}: {C_CODE} ======")

    for REPORT_TYPE in ["pl", "bs"]:
        print(f"============ begin type: {REPORT_TYPE}")
        
        data = crawler.getData(C_CODE, by="company_code", report_type=REPORT_TYPE)

        if REPORT_TYPE == "pl":
            report_comp = "IncomeStatement"
        elif REPORT_TYPE == "bs":
            report_comp = "BalanceSheet"
        with open(
            ROOT_PATH + f"/{f_code}_{report_comp}.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows([[k] + v for k, v in data.items()])
    print(f"====== END {f_code}======")
