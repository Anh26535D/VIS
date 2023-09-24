import requests
import pandas as pd
import json
import os

from bs4 import BeautifulSoup


import sys
import codecs

try:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
except:
    pass


class CompaniesmarketcapCrawler:
    base_url = "https://companiesmarketcap.com"

    def __init__(self) -> None:
        pass

    @staticmethod
    def getDividendCheckList(symbols, check_path):
        data = [
            {
                "Symbol": "Total",
                "Crawl_DividendCash": 0,
                "Crawl_DividendShares": 0,
                "DividendCash": 0,
                "DividendShares": 0,
                "Total": "",
            },
        ]

        for symbol in symbols:
            data_row = {
                "Symbol": symbol,
                "Crawl_DividendCash": 0,
                "Crawl_DividendShares": 0,
                "DividendCash": 0,
                "DividendShares": 0,
                "Total": 0,
            }

            file_path = os.path.join(check_path, f"{data_row['Symbol']}.csv")
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                if not df.empty or (df.shape[0] > 0):
                    data_row["Crawl_DividendCash"] = 1
                    data_row["Crawl_DividendShares"] = 1
                    if "Dividends" in df["Data_type"].unique():
                        data_row["DividendCash"] = 1
                    if "Splits" in df["Data_type"].unique():
                        data_row["DividendShares"] = 1

            data_row["Total"] = data_row["Crawl_DividendCash"] + data_row["Crawl_DividendShares"] + \
                data_row["DividendCash"] + data_row["DividendShares"]

            data[0]["Crawl_DividendCash"] += data_row["Crawl_DividendCash"]
            data[0]["Crawl_DividendShares"] += data_row["Crawl_DividendShares"]
            data[0]["DividendCash"] += data_row["DividendCash"]
            data[0]["DividendShares"] += data_row["DividendShares"]
            data.append(data_row)
        return pd.DataFrame(data)


    def getDividendAndSplitData(self, symbol="14d"):
        symbol = symbol.lower()
        response = requests.get(f"{self.base_url}/api.php?action=search&query={symbol}")
        if response.status_code == 200:
            response_content = json.loads(response.content)
            try:
                symbol_url = ""
                for result in response_content:
                    if symbol in result["identifier"].lower():
                        symbol_url = result["url"]
                if not symbol_url:
                    return pd.DataFrame(), f"Wrong symbol"
                
                dividend_url = self.base_url + "/" + symbol_url + "/dividends"
                dividend_response = requests.get(dividend_url)
                try:
                    dividend_soup = BeautifulSoup(dividend_response.content, 'html.parser')
                    dividend_all_tables = dividend_soup.find_all("table")
                    dividend_df = pd.read_html(str(dividend_all_tables[1]))[0]
                    for table in dividend_all_tables:
                        if ("Date" in str(table)) or ("date" in str(table)):
                            dividend_df = pd.read_html(str(table))[0]
                            break
                    dividend_df["Data_type"] = "Dividends"
                    dividend_df["Value"] = dividend_df["Dividend (stock split adjusted)"]
                    dividend_df.drop(["Dividend (stock split adjusted)", "Change"], axis=1, inplace=True)

                    split_url = self.base_url + "/" + symbol_url + "/stock-splits"
                    split_response = requests.get(split_url)
                    try:
                        split_soup = BeautifulSoup(split_response.content, 'html.parser')
                        split_all_tables = split_soup.find_all("table")
                        split_df = pd.read_html(str(split_all_tables[0]))[0]
                        for table in split_all_tables:
                            if ("Date" in str(table)) or ("date" in str(table)):
                                split_df = pd.read_html(str(table))[0]
                                break
                        split_df["Data_type"] = "Splits"
                        split_df["Value"] = split_df["Split"]
                        split_df.drop(["Split", "Multiple", "Cumulative multiple"],
                                        axis=1, inplace=True)
                        returned_df = pd.concat([dividend_df, split_df]).sort_values("Date", ascending=False).reset_index(drop=True)
                        return returned_df, "OK"
                    except:
                        return pd.DataFrame(), f"Cannot find split data from symbol {symbol}"
                except:
                    return pd.DataFrame(), f"Cannot find dividend data from symbol {symbol}" 
            except IndexError:
                return pd.DataFrame(), f"Cannot find url from symbol {symbol}"
        return pd.DataFrame(), f"Status code is {response.status_code}"