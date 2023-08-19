from IrbankCrawler import IrbankCrawler
import pandas as pd
import os

IGNORE_FLAG = False
# IGNORE_FLAG controls whether existing files should be re-crawled.
# Set IGNORE_FLAG to True if you wish to skip crawling already processed files.

ROOT_PATH = "E:/vis/vis_repo/2023-06/IrbankCrawler"

PL_SAVE_DIR = os.path.join(ROOT_PATH, "Financial_extra", "IncomeStatement")
BS_SAVE_DIR = os.path.join(ROOT_PATH, "Financial_extra", "BalanceSheet")

LIST_COMPANIES_PATH = os.path.join(ROOT_PATH, "codes_2.csv")

companyIDs = pd.read_csv(LIST_COMPANIES_PATH)

crawler = IrbankCrawler(browser="edge")

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
        
        data = crawler.getData(code, by="company_code", report_type=REPORT_TYPE)
        if REPORT_TYPE == "pl":
            save_path = os.path.join(PL_SAVE_DIR, f"{symbol}.csv")
        elif REPORT_TYPE == "bs":
            save_path = os.path.join(BS_SAVE_DIR, f"{symbol}.csv")
        
        data.to_csv(save_path, index=False)

    print(f"====== END {symbol}======")
