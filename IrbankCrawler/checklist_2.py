import pandas as pd
import os

ROOT_PATH = "E:/vis/vis_repo/2023-06/IrbankCrawler/Financial_2"
LIST_COMPANIES_PATH = "E:/vis/vis_repo/2023-06/IrbankCrawler/codes.csv"
companyIDs = pd.read_csv(LIST_COMPANIES_PATH)

result = pd.DataFrame(
)

result["symbol"] = companyIDs["fcode"].sort_values().astype("str")

def extract_year(date_string):
    start_index = date_string.find('年')
    if start_index != -1:
        year = date_string[start_index - 4: start_index]
        return year
    return None

for doc_type in ("IncomeStatement", "BalanceSheet"):
    result[f"{doc_type}_path"] = ROOT_PATH + "/" + doc_type + "/" + result["symbol"] + ".csv"

result[f"IncomeStatement"] = result.apply(
    lambda row: 
    [extract_year(date_string) for date_string in pd.read_csv(row[f"IncomeStatement_path"], nrows=1).columns.to_list()[1:]] 
    if (os.path.exists(row[f"IncomeStatement_path"]) and os.path.getsize(row[f"IncomeStatement_path"]) > 0) 
    else "", 
    axis=1
)

result[f"BalanceSheet"] = result.apply(
    lambda row: 
    [str(int(extract_year(date_string))-1) for date_string in pd.read_csv(row[f"BalanceSheet_path"], nrows=1).columns.to_list()[1:]] 
    if (os.path.exists(row[f"BalanceSheet_path"]) and os.path.getsize(row[f"BalanceSheet_path"]) > 0) 
    else "", 
    axis=1
)

result = result.drop(["IncomeStatement_path", "BalanceSheet_path"], axis=1)
result["Document_Counter"] = result["IncomeStatement"] + result["BalanceSheet"]
result = result.drop(["IncomeStatement", "BalanceSheet"], axis=1)

YEAR_COLS = [str(year) for year in range(2000, 2024)]
COLUMNS = ["symbol"] + YEAR_COLS
counter_df = pd.DataFrame(columns=COLUMNS)
counter_df["symbol"] = result["symbol"]
counter_df[YEAR_COLS] = 0

for i in range(counter_df.shape[0]):
    for v in result.loc[i, "Document_Counter"]:
        if v in counter_df.columns:
            counter_df.loc[i, v] += 1

sumary_row = pd.DataFrame(
    [["Total"] + ["0"]*len(YEAR_COLS)],
    columns=COLUMNS
)
for year_col in YEAR_COLS:
    sumary_row.loc[0, year_col] = counter_df[year_col].sum()

result = pd.concat([sumary_row, counter_df])
result.to_excel("checklist_financial_year_DamVietAnh.xlsx", index=False)
