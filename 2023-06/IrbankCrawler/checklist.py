import os
import pandas as pd

PATH = "G:/.shortcut-targets-by-id/15-cUFhSiV6ag8MQktsfieL9O58MEh4eO/Financial"

delist_after_ccode = pd.read_csv("G:/My Drive/IrbankCrawler/delist_after_ccode.csv")
delist_before_ccode = pd.read_csv("G:/My Drive/IrbankCrawler/delist_before_ccode.csv")
ccode = pd.read_csv("G:/My Drive/IrbankCrawler/ccode.csv")

full_ccode = pd.concat([ccode, delist_before_ccode, delist_after_ccode])

full_ccode = full_ccode.sort_values(["fcode"]).reset_index().drop(["index"], axis=1).drop_duplicates()
f_codes = full_ccode["fcode"]
full_ccode = full_ccode.set_index(["fcode"])
full_ccode["Income_Statement"] = ""
full_ccode["Balance_Sheet"] = ""

for doc_type in ("IncomeStatement", "BalanceSheet"):
    pl_path = PATH + "/" + doc_type
    for f_code in f_codes:
        file_path = pl_path + f"/{f_code}.csv"
        if not os.path.isfile(file_path):
            full_ccode[doc_type].loc[f_code] = 0
        else:
            size = os.path.getsize(file_path)
            if size > 0:
                full_ccode[doc_type].loc[f_code] = 1
            else:
                full_ccode[doc_type].loc[f_code] = 0
        print(f"DONE WITH {f_code}")

full_ccode.to_csv("checklist.csv")

