from IrbankCrawler import IrbankCrawler
import pandas as pd
import os

ROOT_PATH = "E:/vis/vis_repo/2023-06/IrbankCrawler"
SAVE_PATH = ROOT_PATH + "/Financial_test"
LIST_COMPANIES_PATH = ROOT_PATH + "/" + "missing_company.csv"
LINK_PATH = "E:/vis/vis_repo/2023-06/IrbankCrawler/Link_financial"

companyIDs = pd.read_csv(LIST_COMPANIES_PATH)

crawler = IrbankCrawler(browser="edge")

crawled_pl_symbols = os.listdir(SAVE_PATH + "/IncomeStatement")
crawled_bs_symbols = os.listdir(SAVE_PATH + "/BalanceSheet")
for symbol, code in companyIDs[["Symbol", "Code"]].to_numpy():
    print(f"====== BEGIN {symbol}: {code} ======")

    for REPORT_TYPE in ["pl", "bs"]:
        if ((REPORT_TYPE == "pl") and (str(symbol) + ".csv" not in crawled_pl_symbols)) \
            or \
            ((REPORT_TYPE == "bs") and (str(symbol) + ".csv" not in crawled_bs_symbols)):

            print(f"============ begin type: {REPORT_TYPE}")
            try:
                links = pd.read_csv(f"{LINK_PATH}/{code}.csv")["通期"]
            except FileNotFoundError as fnf_error:
                print(f"Not found file {code}.csv")
            dfs = []
            for i, link in enumerate(links):
                print(i, end=" ")
                if "pl" in link:
                    if (i == len(links) - 1) or ("pl" not in links[i+1]):
                        useAllColumns = True
                    else:
                        useAllColumns = False
                    if REPORT_TYPE == "bs":
                        link = link.replace("pl", "bs")
                    dt_tables = crawler.getDataFromLink(link, useAllColumns)
                    dfs.extend(dt_tables)
            print()
            try:
                data = crawler.concatData(dfs)
            except:
                data = pd.DataFrame()

            if REPORT_TYPE == "pl":
                report_comp = "IncomeStatement"
            elif REPORT_TYPE == "bs":
                report_comp = "BalanceSheet"

            data.to_csv(f"{SAVE_PATH}/{report_comp}/{symbol}.csv", index=False)
    print(f"====== END {symbol}======")
