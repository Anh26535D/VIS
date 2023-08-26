import requests
import pandas as pd
import json
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver import edge

import sys
import codecs

try:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
except:
    pass


class MorningStartCrawler:
    base_url = "https://www.morningstar.com/stocks/xasx/"
    bear_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1EY3hOemRHTnpGRFJrSTRPRGswTmtaRU1FSkdOekl5TXpORFJrUTROemd6TWtOR016bEdOdyJ9.eyJodHRwczovL21vcm5pbmdzdGFyLmNvbS9tc3Rhcl9pZCI6IkM5NEE5NzE0LTlDNTMtNEFDRS1BQ0YyLTA1NkM0N0YzOTUwQiIsImh0dHBzOi8vbW9ybmluZ3N0YXIuY29tL2VtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiaHR0cHM6Ly9tb3JuaW5nc3Rhci5jb20vZW1haWwiOiJyZXNlYXJjaDEwMDFAbXN0YXIuY29tIiwiaHR0cHM6Ly9tb3JuaW5nc3Rhci5jb20vcm9sZSI6WyJMaWNlbnNlLlJpc2tNb2RlbEFkdmFuY2VkIiwiUFMuQ2FuUHVibGlzaFRlbXBsYXRlIiwiVmVsb1VJLkFsbG93QWNjZXNzIl0sImh0dHBzOi8vbW9ybmluZ3N0YXIuY29tL2NvbXBhbnlfaWQiOiJhM2Q2NTc0OC1iNDdlLTRkM2EtOWZjNi04MDZhOGMwM2Y0YjciLCJodHRwczovL21vcm5pbmdzdGFyLmNvbS9pbnRlcm5hbF9jb21wYW55X2lkIjoiQ2xpZW50MCIsImh0dHBzOi8vbW9ybmluZ3N0YXIuY29tL2RhdGFfcm9sZSI6WyJRUy5NYXJrZXRzIiwiUVMuUHVsbHFzIl0sImh0dHBzOi8vbW9ybmluZ3N0YXIuY29tL2NvbmZpZ19pZCI6Ik1TRVJQX1FTX1BST0YiLCJodHRwczovL21vcm5pbmdzdGFyLmNvbS91aW1fcm9sZXMiOiJPRkZJQ0VfRlJFRSxBUkNfRlVORFMsRUFNUyxBSV9NRU1CRVJfMV8wLEFVX01FTUJFUl8xXzAsSUNfTUVNQkVSXzJfMCxNRF9NRU1CRVJfMV8xLFJRX01FTUJFUl8xXzEsRk5fTUVNQkVSXzFfMCxBUkNfTUFSS0VUUyxTRV9NRU1CRVJfMl8wLEFVQVJDX1VTRVIsQ0FfTUVNQkVSXzFfMCxBUkNfQ1JFRElULEZEX01FTUJFUl8xXzEwMDAwMDAxMDAsVUtfTUVNQkVSXzFfMCxETV9NRU1CRVJfMV8wLEFSQ19FVEYsQVJDX0VRVUlUWSxNVV9NRU1CRVJfMV8wLE1JX01FTUJFUl8xXzAsRE9UX0NPTV9QUkVNSVVNIiwiaXNzIjoiaHR0cHM6Ly9sb2dpbi1wcm9kLm1vcm5pbmdzdGFyLmNvbS8iLCJzdWIiOiJhdXRoMHxDOTRBOTcxNC05QzUzLTRBQ0UtQUNGMi0wNTZDNDdGMzk1MEIiLCJhdWQiOlsiaHR0cHM6Ly9hdXRoMC1hd3Nwcm9kLm1vcm5pbmdzdGFyLmNvbS9tYWFzIiwiaHR0cHM6Ly91aW0tcHJvZC5tb3JuaW5nc3Rhci5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNjkyOTgwODY3LCJleHAiOjE2OTI5ODQ0NjcsImF6cCI6ImlRa1d4b2FwSjlQeGw4Y0daTHlhWFpzYlhWNzlnNjRtIiwic2NvcGUiOiJvcGVuaWQiLCJndHkiOiJwYXNzd29yZCJ9.sgIDZiT2pUTeedLuyH58OLZB9v0c5923TsmmwREKwuqUCHxbWj_gFas_-20HZmuISeh3DZGT_JcCrqs7k0Qb3iAUo4BcvHciq6RnHbT5rOXdiWoEbxAo95kkfxGMaP10FN0KoM1f6dooLoytSpXDl0T4kT5X03U4UVFJK-_Mbq1P0qg15EmbCQG4UgntvCR0Y7xQWdsMi0szWRU_Rt8TqgfLS_W3bhtn1snSN-nRPwJx_EGgvxmbNgP0bKbgNR01lo_KAfjODn4bMT2X2OowApiif-txG0wcMdA35O72dbaqoCB3zV4NwBVx5D68w84gyjcAidU5bOVD5wtf0U6t1Q"

    def __init__(self, bear_token=None) -> None:
        self.options = edge.options.Options()
        self.options.add_argument("--headless=new")
        self.resetDriver()

        self.bear_token = bear_token

    def resetDriver(self):
        self.driver = webdriver.Edge(options=self.options)

    def closeDriver(self):
        self.driver.close()

    def getPriceData(self, symbol="14d", startDate="2000-01-01", endDate="2023-08-23"):
        self.resetDriver()

        self.driver.get(f"https://www.morningstar.com/stocks/xasx/{symbol}/chart")
        try:
            security_id = self.driver.find_element(by=By.TAG_NAME, value="sal-components").get_attribute("security-id")
        except NoSuchElementException:
            return pd.DataFrame(), "Cannot find tagname `sal-components` with attribute `security-id`"

        self.closeDriver()

        url = "https://www.us-api.morningstar.com/QS-markets/chartservice/v2/timeseries"
        request_params = {
            "query": f"{security_id}:open,high,low,close,volume,previousClose",
            "frequency": "d",
            "startDate": startDate,
            "endDate": endDate,
            "trackMarketData": "3.6.3",
            "instid": "MSERP",
        }

        request_headers = {
            "Authorization": f"Bearer {self.bear_token}"
        }

        response = requests.get(url, params=request_params, headers=request_headers)
        if response.status_code == 200:
            response_content = json.loads(response.content)
            try:
                return pd.DataFrame(response_content[0]["series"]), "OK"
            except:
                return pd.DataFrame(), "Something wrong"
        return pd.DataFrame(), "Status code is not 200. Your bearer token might be expired."