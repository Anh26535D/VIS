import requests
import pandas as pd
import json
from time import sleep

from typing import Tuple

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver import edge
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import codecs

try:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
except:
    pass


class MorningStarCrawler:
    base_url = "https://www.morningstar.com/stocks/xasx"

    def __init__(self, bear_token=None) -> None:
        self.options = edge.options.Options()
        self.options.add_argument("--headless=new")
        self.resetDriver()

        self.bear_token = bear_token

    def resetDriver(self) -> None:
        self.driver = webdriver.Edge(options=self.options)

    def closeDriver(self) -> None:
        self.driver.close()

    def isPageExist(self, url) -> bool:
        text_to_check = "Like guarantees of future returns, this page doesn’t exist."
        self.resetDriver()
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 5).until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), text_to_check))
            self.closeDriver()
            return False
        except:
            self.closeDriver()
            return True


    def getPriceDataFromAPI(self, symbol="14d", startDate="2000-01-01", endDate="2023-08-23") -> Tuple[pd.DataFrame, str]:
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

    def getPriceData(self, symbol="bhp", timeout=300) -> Tuple[pd.DataFrame, str]:
        url = f"{self.base_url}/{symbol}/chart"
        if not self.isPageExist(url):
            return pd.DataFrame(), "Page not found"
        
        self.resetDriver()
        self.driver.get(url)

        while timeout>0:
            try:
                range_buttons = self.driver.find_elements(by=By.CSS_SELECTOR, value='button[class="mds-button___markets mds-button--flat___markets markets-ui-button mwc-markets-chart-time-interval__btn"]')
                range_buttons[-1].click()
                break
            except IndexError as idxerror:
                timeout -= 1
                sleep(1)
                continue
        if timeout == 0:
            return pd.DataFrame(), "Time is out when finding range button"

        freq_select = self.driver.find_element(by=By.CSS_SELECTOR, value='select[class="mds-select__input___markets"]')
        Select(freq_select).select_by_value("d")

        table_button = self.driver.find_element(by=By.CSS_SELECTOR, value='button[aria-label="Table"][class="mds-button___markets mds-button--icon-only___markets mds-button--large___markets markets-ui-button"]')
        table_button.click()

        market_select = self.driver.find_elements(by=By.CSS_SELECTOR, value='select[class="mds-select__input___markets"]')
        Select(market_select[1]).select_by_value("priceVolumeDetail")

        while timeout>0:
            try:
                market_select = self.driver.find_elements(by=By.CSS_SELECTOR, value='select[class="mds-select__input___markets"]')
                Select(market_select[3]).select_by_value("-1")
                break
            except IndexError as idxerror:
                timeout -= 1
                sleep(1)
                continue
        if timeout == 0:
            return pd.DataFrame(), "Time is out when setting -1"
        
        while timeout>0:
            try:
                div_table = self.driver.find_element(by=By.CSS_SELECTOR, value='div[class="mwc-markets-chart-table"]')
                table = div_table.find_element(by=By.TAG_NAME, value="table")
                break
            except NoSuchElementException as noeleexcept:
                timeout -= 1
                sleep(1)
                continue
        if timeout == 0:
            return pd.DataFrame(), "Time is out when finding table"

        html_table = table.get_attribute("outerHTML")
        data = pd.read_html(html_table)[0]
        data["Date"] = pd.to_datetime(data["Date"])

        self.closeDriver()

        return data, "OK"