import requests
from io import StringIO
import pandas as pd
import sys
import codecs

try:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
except:
    pass


class IntelligentInvestorCrawler:
    base_url = "https://www.intelligentinvestor.com.au/shares"

    def __init__(self) -> None:
        pass

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
            try:
                df["Date"] = pd.to_datetime(df["Date"])
                return df, "OK"
            except:
                return pd.DataFrame(), "Cannot convert Date column to datetime or the response does not contain Date column"
        else:
            return pd.DataFrame(), "Response status is not 200"
