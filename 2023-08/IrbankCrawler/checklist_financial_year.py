import pandas as pd
import os

ROOT_PATH = "E:/vis/vis_repo/2023-06/IrbankCrawler/Financial_2"
LIST_COMPANIES_PATH = "E:/vis/vis_repo/2023-06/IrbankCrawler/codes.csv"
companyIDs = pd.read_csv(LIST_COMPANIES_PATH)

result = pd.DataFrame()

result["symbol"] = companyIDs["Symbol"].sort_values().astype("str")

def extract_year(date_string, isPl=False):
    start_index = -1
    n_occurence = 0
    for i, char in enumerate(date_string):
        if char == '年':
            if n_occurence == 1:
                start_index = i
                break
            else:
                if not isPl:
                    start_index = i
                    break
                n_occurence += 1
    if start_index != -1:
        year = date_string[start_index - 4: start_index]
        return year
    return None

for doc_type in ("IncomeStatement", "BalanceSheet"):
    result[f"{doc_type}_path"] = ROOT_PATH + "/" + doc_type + "/" + result["symbol"] + ".csv"

def func_(row):
    try:
        if (os.path.exists(row)) and (os.path.getsize(row) > 0):
            tmp_df = pd.read_csv(row, nrows=1).columns.to_list()[1:]
            return [extract_year(date_string, True) for date_string in tmp_df]
        else:
            return ""
    except:
        return ""
result["IncomeStatement"] = result["IncomeStatement_path"].apply(func=func_)


def func_(row):
    try:
        if (os.path.exists(row)) and (os.path.getsize(row) > 0):
            tmp_df = pd.read_csv(row, nrows=1).columns.to_list()[1:]
            return [str(int(extract_year(date_string))) for date_string in tmp_df]
        else:
            return ""
    except:
        return ""
result[f"BalanceSheet"] = result["BalanceSheet_path"].apply(func=func_)

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
