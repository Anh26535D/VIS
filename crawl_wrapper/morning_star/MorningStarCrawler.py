import requests
import pandas as pd
import json
from time import sleep
import os
import pyautogui
import numpy as np
from bs4 import BeautifulSoup

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

    error_code_info = {
        "M100": "OK",
        "M101": "Your bearer token might be expired.",
        "M102": "Cannot find tagname `sal-components` with attribute `security-id`",
        "M103": "Cannot find tagname `dividend` in response content",
        "M104": "Cannot find tagname `split` in response content",
        "M105": "Cannot find tagname `dividend` and `split` in response content",
        "M106": "The response has no content",
        "M404": "Page not found",
        "M500": "Undefined error",
    }

    def __init__(self, bearer_token=None, apikey=None) -> None:
        self.options = edge.options.Options()
        self.options.add_argument("--headless=new")
        self.resetDriver()

        self.bearer_token = bearer_token
        self.apikey = apikey

    def resetDriver(self) -> None:
        self.driver = webdriver.Edge(options=self.options)

    def closeDriver(self) -> None:
        self.driver.close()

    @staticmethod
    def getPriceCheckList(symbols, check_path):
        data = [{
            "Symbol": "Total",
            "Crawl_Price": 0,
            "Price": 0,
            "Date_Start": "",
            "Date_End": "",
        }]

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
                    df["date"] = pd.to_datetime(
                        df["date"]).dt.strftime('%d/%m/%Y')
                    data_row["Price"] = 1
                    data_row["Date_Start"] = df.loc[0, "date"]
                    data_row["Date_End"] = df.loc[df.shape[0]-1, "date"]
                else:
                    data_row["Price"] = 0
            else:
                data_row["Crawl_Price"] = 0
                data_row["Price"] = 0

            data[0]["Crawl_Price"] += data_row["Crawl_Price"]
            data[0]["Price"] += data_row["Price"]
            data.append(data_row)
        return pd.DataFrame(data)

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
    
    # @staticmethod
    # def getSecurityID(symbol):
    #     options = edge.options.Options()
    #     options.add_argument("--headless=new")
    #     driver = webdriver.Edge(options=options)
    #     driver.get(
    #         f"https://www.morningstar.com/stocks/xasx/{symbol}/chart")
    #     try:
    #         security_id = driver.find_element(
    #             by=By.TAG_NAME, value="sal-components").get_attribute("security-id")
    #         driver.close()
    #         return security_id, 100
    #     except NoSuchElementException:
    #         driver.close()
    #         return "", 102

    @staticmethod
    def getSecurityID(symbol):
        response = requests.get(f"https://www.morningstar.com/stocks/xasx/{str(symbol).lower()}/chart")
        if response.status_code == 200:
            content = response.content.decode()
            soup = BeautifulSoup(content, "html.parser")
            script_tags = soup.find_all("script")
            match_text = ""
            for script_tag in script_tags:
                if "window.__NUXT__" in script_tag.text:
                    match_text = script_tag.text
                    break
            match_text = match_text.split("(")[-1]
            match_idx = match_text.find("0P00")
            match_text = match_text[match_idx:match_idx+10]
            return match_text, "M100"
        else:
            return "", f"M{response.status_code}"

    def isPageExist(self, url, check_text="Like guarantees of future returns, this page doesn’t exist.") -> bool:
        self.resetDriver()
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), check_text))
            self.closeDriver()
            return False
        except:
            self.closeDriver()
            return True

    def check_bearer_token(self, log_entry):
        if "params" in log_entry and "headers" in log_entry["params"]:
            headers = log_entry["params"]["headers"]
            return "Authorization: Bearer" in headers
        return False

    def check_apikey(self, log_entry):
        if "params" in log_entry and "headers" in log_entry["params"]:
            headers = log_entry["params"]["headers"]
            return "ApiKey:" in headers
        return False

    def resetNetExportLogFile(self, log_file_path, wait_time, url_log):
        if os.path.exists(log_file_path):
            os.remove(log_file_path)

        driver = webdriver.Edge()
        driver.get("edge://net-export/")
        try:
            driver.find_element(By.ID, "start-logging").click()
        except NoSuchElementException as ex:
            driver.find_element(By.ID, "startover").click()
            driver.find_element(By.ID, "start-logging").click()

        sleep(1)
        pyautogui.write(log_file_path)
        pyautogui.press("enter")

        driver.execute_script("window.open('', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(url_log)

        sleep(wait_time)

        driver.switch_to.window(driver.window_handles[0])
        driver.close()
        driver.quit()

    def resetBearerToken(self, log_file_path, wait_time=10):
        self.resetNetExportLogFile(log_file_path, wait_time, "https://www.morningstar.com/stocks/xasx/14d/chart")

        with open(log_file_path, "r") as f:
            log_entries = json.load(f)
        event_entries = log_entries["events"]
        for entry in event_entries:
            if self.check_bearer_token(entry):
                lst_header_params = entry["params"]["headers"].split("\r\n")
                for header_param in lst_header_params:
                    if "Authorization: Bearer" in header_param:
                        self.bearer_token = header_param.split()[2]
                        return True
        return False

    def resetAPIKey(self, log_file_path, wait_time=10):
        self.resetNetExportLogFile(log_file_path, wait_time, "https://www.morningstar.com/stocks/xasx/14d/financials")

        with open(log_file_path, "r") as f:
            log_entries = json.load(f)
        event_entries = log_entries["events"]
        for entry in event_entries:
            if self.check_apikey(entry):
                lst_header_params = entry["params"]["headers"].split("\r\n")
                for header_param in lst_header_params:
                    if "ApiKey:" in header_param:
                        self.apikey = header_param.split()[1]
                        return True
        return False

    def getPriceDataFromAPI(self, symbol="14d", security_id=None, startDate="2000-01-01", endDate="2023-08-23") -> Tuple[pd.DataFrame, str]:
        if security_id is None:
            security_id, error_code = self.getSecurityID(symbol)
        else:
            error_code = "M100"
        if error_code == "M100":
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
                "Authorization": f"Bearer {self.bearer_token}"
            }

            response = requests.get(
                url, params=request_params, headers=request_headers)
            if response.status_code == 200:
                response_content = json.loads(response.content)
                try:
                    return pd.DataFrame(response_content[0]["series"]), "M100"
                except:
                    return pd.DataFrame(), "Something wrong"
            return pd.DataFrame(), "M101"
        else:
            return pd.DataFrame(), error_code

    def getDividendAndSplitDataFromAPI(self, symbol="14d", security_id=None, startDate="2000-01-01", endDate="2023-08-23") -> Tuple[pd.DataFrame, str]:
        if security_id is None:
            security_id, error_code = self.getSecurityID(symbol)
        else:
            error_code = "M100"
        if error_code == "M100":
            url = "https://www.us-api.morningstar.com/QS-markets/chartservice/v2/timeseries"
            request_params = {
                "query": f"{security_id}:dividend,split",
                "frequency": "d",
                "startDate": startDate,
                "endDate": endDate,
                "trackMarketData": "3.6.3",
                "instid": "MSERP",
            }

            request_headers = {
                "Authorization": f"Bearer {self.bearer_token}"
            }

            response = requests.get(
                url, params=request_params, headers=request_headers)
            if response.status_code == 200:
                response_content = json.loads(response.content)
                if response_content[0]["queryKey"] == "nan":
                    return pd.DataFrame(), "M106"
                error_code = "M100"
                try:
                    dividend_df = pd.DataFrame(response_content[0]["events"]["dividend"])
                    dividend_df["Date"] = dividend_df["date"]
                    dividend_df["Data_type"] = "Dividends"
                    dividend_df["Value"] = dividend_df["value"]
                    dividend_df.drop(["date", "value"], axis=1, inplace=True)
                except:
                    dividend_df = pd.DataFrame(columns=["Date", "Data_type", "Value"])
                    error_code = "M103"

                try:
                    split_df = pd.DataFrame(response_content[0]["events"]["split"])
                    split_df["Date"] = split_df["date"]
                    split_df["Data_type"] = "Splits"
                    split_df["Value"] = split_df["postSplitShare"].astype(
                        str) + ":" + split_df["preSplitShare"].astype(str)
                    split_df.drop(["date", "postSplitShare",
                                "preSplitShare"], axis=1, inplace=True)
                except:
                    split_df = pd.DataFrame(columns=["Date", "Data_type", "Value"])
                    if error_code == "M103":
                        error_code = "M105"
                    else:
                        error_code = "M104"

                try:
                    returned_df = pd.concat([dividend_df, split_df]).sort_values(
                        "Date", ascending=False).reset_index(drop=True)
                    if error_code in ("M100", "M103", "M104"):
                        error_code = "M100"
                    return returned_df, error_code
                except:
                    return pd.DataFrame(), "M500"
            return pd.DataFrame(), "M101"
        else:
            return pd.DataFrame(), error_code

    def saveFinancialData(self, symbol="bhp", security_id=None, save_dir=None, type="incomeStatement", apikey="lstzFDEOhfFNMLikKa0am9mgEKLBl49T"):
        if security_id is None:
            security_id, error_code = self.getSecurityID(symbol)
        else:
            error_code = "M100"
        if error_code == "M100":
            service_base_url = "https://api-global.morningstar.com/sal-service/v1/"
            extend_url = f"stock/newfinancials/{security_id}/{type}/detail"
            params = "?dataType=A&reportType=A&locale=en&operation=export"

            url = service_base_url + extend_url + params

            headers = {
                "accept-language": "en-US,en;q=0.9",
                "apikey": apikey,
                "content-type": "application/vnd.ms-excel",
                "origin": "https://www.morningstar.com",
                "referer": f"https://www.morningstar.com/stocks/xasx/{symbol}/financials",
                "sec-ch-ua": '"Microsoft Edge";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "accept": "*/*"
            }

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                file_name = f"{symbol}.xls"
                try:
                    with open(os.path.join(save_dir, file_name), "wb") as file:
                        file.write(response.content)
                        return True, "M100"
                except TypeError:
                    print(response.content)
                    return False, "Fail with NoneType return"
            else:
                return False, f"Fail with status code {response.status_code}"
        else:
            return False, error_code