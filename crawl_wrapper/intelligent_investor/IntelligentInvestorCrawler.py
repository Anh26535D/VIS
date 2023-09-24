import requests
from io import StringIO
import pandas as pd
import sys
import codecs
import numpy as np
import os

try:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
except:
    pass


class IntelligentInvestorCrawler:
    base_url = "https://www.intelligentinvestor.com.au/shares"
    date_formats =  ["%d %b %Y", "%d %B %Y"]

    def __init__(self) -> None:
        pass

    @staticmethod
    def getCheckList(symbols, check_path):
        data = []
        summary_row = {
            "Symbol": "Total",
            "Crawl_Price": 0,
            "Price": 0,
            "Date_Start": "",
            "Date_End": "",
        }
        data.append(summary_row)

        for i in range(len(symbols)):
            data_row = {
                "Symbol": "",
                "Crawl_Price": "",
                "Price": "",
                "Date_Start": np.nan,
                "Date_End": np.nan,
            }

            data_row["Symbol"] = symbols[i]
            file_path = os.path.join(check_path, f"{data_row['Symbol']}.csv")
            if os.path.exists(file_path):
                data_row["Crawl_Price"] = 1
                df = pd.read_csv(file_path)
                if not df.empty or (df.shape[0] > 0):
                    df["Date"] = pd.to_datetime(
                        df["Date"]).dt.strftime('%d/%m/%Y')
                    data_row["Price"] = 1
                    data_row["Date_Start"] = df.loc[0, "Date"]
                    data_row["Date_End"] = df.loc[df.shape[0]-1, "Date"]
                else:
                    data_row["Price"] = 0
            else:
                data_row["Crawl_Price"] = 0
                data_row["Price"] = 0

            data[0]["Crawl_Price"] += data_row["Crawl_Price"]
            data[0]["Price"] += data_row["Price"]
            data.append(data_row)
        return pd.DataFrame(data)

    def getPriceData(self, symbol="14d", startDate="01/01/2000", endDate="23/08/2023"):
        symbol = symbol.lower()
        url = f"{self.base_url}/asx-{symbol}/1/share-price"

        form_data = {
            "From": startDate,
            "To": endDate,
            "download-csv": "Download"
        }

        response = requests.post(url, data=form_data)

        if response.status_code == 200:
            content = response.content.decode()
            try:
                df = pd.read_csv(StringIO(content))
            except:
                return pd.DataFrame(), "Cannot convert response content to dataframe"
            
            for format_str in self.date_formats:
                try:
                    df["Date"] = pd.to_datetime(df["Date"], format=format_str)
                    return df, "OK"
                except:
                    pass
            return pd.DataFrame(), "Cannot convert Date column to datetime or the response does not contain Date column"
        
        else:
            return pd.DataFrame(), "Response status is not 200"
