import requests
import json
from datetime import datetime
import pandas as pd
from dateutil import relativedelta

class CafefCrawler:
    def __init__(self) -> None:
        pass

    def getPrice(symbol, startDate=None, endDate=None, yrsDelta=1):
        symbol = symbol.upper()
        base_url = "https://s.cafef.vn/Ajax/PageNew/DataHistory/PriceHistory.ashx"
        if endDate is None:
            endDate = datetime.today().strftime('%m/%d/%Y')
        if startDate is None:
            startDate = datetime.now() - relativedelta(years=yrsDelta)
            startDate = startDate.strftime('%m/%d/%Y')
        params = {
            "Symbol": symbol,
            "StartDate": startDate,
            "EndDate": endDate,
            "PageIndex": "1",
            "PageSize": "100000"
        }

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            content = json.loads(response.content)
            data = content["Data"]["Data"]
            data = pd.DataFrame(data)
        else:
            data = pd.DataFrame()
        return data