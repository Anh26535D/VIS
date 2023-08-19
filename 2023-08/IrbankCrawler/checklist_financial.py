import pandas as pd
import os

ROOT_PATH = "E:/vis/vis_repo/2023-06/IrbankCrawler/Financial_2"
LIST_COMPANIES_PATH = "E:/vis/vis_repo/2023-06/IrbankCrawler/codes.csv"
companyIDs = pd.read_csv(LIST_COMPANIES_PATH)

COLUMNS = ["symbol", "Crawl_BalanceSheet", "Crawl_IncomeStatement", "BalanceSheet", "IncomeStatement", "Total"]

sumary_row = pd.DataFrame(
    [["Total", 0, 0, 0, 0, ""]],
    columns=COLUMNS
)

result = pd.DataFrame(
    columns=COLUMNS
)
result["symbol"] = companyIDs["fcode"].sort_values().astype("str")

for doc_type in ("IncomeStatement", "BalanceSheet"):
    result[f"{doc_type}_path"] = ROOT_PATH + "/" + doc_type + "/" + result["symbol"] + ".csv"
    result[f"Crawl_{doc_type}"] = result.apply(
        lambda row: 1 if os.path.exists(row[f"{doc_type}_path"]) else 0, axis=1)
    result[f"{doc_type}"] = result.apply(
        lambda row: 1 if (os.path.exists(row[f"{doc_type}_path"]) and os.path.getsize(row[f"{doc_type}_path"]) > 0) else 0, axis=1)

result = result.drop(["IncomeStatement_path", "BalanceSheet_path"], axis=1)
result["Total"] = result["IncomeStatement"] + result["BalanceSheet"]

sumary_row.loc[0, "Crawl_BalanceSheet"] = result["Crawl_BalanceSheet"].sum()
sumary_row.loc[0, "Crawl_IncomeStatement"] = result["Crawl_IncomeStatement"].sum()
sumary_row.loc[0, "BalanceSheet"] = result["BalanceSheet"].sum()
sumary_row.loc[0, "IncomeStatement"] = result["IncomeStatement"].sum()


result = pd.concat([sumary_row, result])
result.to_excel("checklist_financial_DamVietAnh.xlsx", index=False)
