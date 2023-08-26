import requests as r
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from collections import Counter
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver import chrome
from selenium.webdriver import edge
import json

import sys
import codecs

try:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
except:
    pass

from CommonLink import CommonLink

class IrbankCrawler:

    def __init__(self, browser="chrome", exe_path=None) -> None:
        self.browser = browser
        self.exe_path = exe_path
        if browser == "edge":
            self.options = edge.options.Options()
            self.options.add_argument("--headless=new")
        elif browser == "chrome":
            self.options = chrome.options.Options()
            self.options.add_argument("--headless=new")
        self.newDriver()
            
    def newDriver(self):
        if self.browser == "edge":
            self.driver = webdriver.Edge(options=self.options)
        elif self.browser == "chrome":
            self.driver = webdriver.Chrome(options=self.options)

    def closeDriver(self):
        self.driver.close()

    def setDocumentLink(self, company_code, document_code, report_type):
        '''Get the document link from company code, document code and report type

            Parameters
            ----------
            company_code : str
                Company code 

            document_code : str
                Document code 

            report_type : str
                Report type
            
            Returns
            -------
            link : str
                Document link
        
        '''
        link = CommonLink.DOCUMENT_LINK
        link = link.replace("company_code", str(company_code))
        link = link.replace("document_code", str(document_code))
        link = link.replace("report_type", str(report_type))
        return link
    
    def setReportLink(self, code):
        '''Get the report link from financial code

            Parameters
            ----------
            code : int
                Financial code 
            
            Returns
            -------
            link : str
                Report link
        
        '''
        link = CommonLink.REPORT_LINK
        link = link.replace("financial_code", str(code))
        return link

    def getCompanyCode(self, f_code):
        '''Get the company code from financial code

            Parameters
            ----------
            f_code : int
                Financial code 
            
            Returns
            -------
            [f_code, c_code] : list with shape of (2,)
                Pair of financial code and company code
        
        '''
        link = self.setReportLink(f_code)
        session = r.Session()
        try:
            response = session.get(link)
            if response.status_code == 200:
                report_url = response.url
                c_code = report_url.split("/")[3]
                return [f_code, c_code]
            else:
                print(f"Something wrong with {f_code}")
                return [None, None]
        except r.exceptions.RequestException:
            return [None, None]

    def getValidDocumentCodes(self, ccode, report_link=None):
        ''' Extract all document codes from financial report link, or from given company code (ccode)

            .. note::
            This method is only work with irbank report link, 
            and with only format like table this link: https://irbank.net/E00015/reports

            Parameters
            ----------
            ccode : str
                Company code 

            report_link : str
                Link to financial report

            Returns
            -------
            report_codes : list
                List of string report codes
        '''
        if report_link is not None:
            link = report_link
        else:
            link = self.setReportLink(ccode)
        rs = r.get(link)
        
        rsp = BeautifulSoup(rs.content, "html.parser")
        table = rsp.find("table")
        stock_slice_batch = pd.read_html(str(table), extract_links="all")[0]
        list_block = table.find_all("td")
        dict_ = {}
        for block in list_block:
            list_a = block.find_all("a")
            try:
                link_basic = list_a[0]["href"]
                link = list_a[-1]["href"]
                key = f"{link_basic}"
                dict_[key] = link
            except:
                pass

        for col in stock_slice_batch.columns[0:5]:
            for row in stock_slice_batch.index:
                t = stock_slice_batch[col][row]
                for key in dict_.keys():
                    if t[1] == key:
                        stock_slice_batch[col][row] = dict_[key]

        fy_report_codes = stock_slice_batch[("通期", None)].to_list()
        fy_old_report_codes = stock_slice_batch[("年度", None)].to_list()
        fy_report_links = fy_report_codes + fy_old_report_codes

        report_codes = []
        for code in fy_report_links:
            if code[-2:] == "pl" and code[:-3] not in report_codes:
                report_codes.append(code[:-3])

        return report_codes

    def normalizeSeries(self, series, delimiter="__"):
        '''Normalize series of string

            Parameters
            ----------
            series : array-like
                List of string need to be normalized
            
            delimiter : str
                The delimiter of each string in series

            Returns
            -------
            series : array-like
                List of normalized string

            Examples
            --------
            Given list of string ["A_B_C", "E_F_C", "A_B_E", "A_F_D"] need normalizing with "_" as delimiter
            The output of this method will be ["A_B_C", "E_F_C", "E", "D"]
            "A_B_C" and "E_F_C" have the the same suffix, so that it will not be changed, whereas "A_B_E", "A_F_D"
            have "E" and "D" different, so that we just keep the suffixes of these.
        '''
        suffix_counts = Counter([v.split(delimiter)[-1] for v in series])
        for i in range(len(series)):
            suff = series[i].split(delimiter)[-1]
            if suffix_counts[suff] == 1:
                series[i] = suff

        count_dict = {}
        new_list = []

        for item in series:
            if item in count_dict:
                count_dict[item] += 1
                new_list.append(f"{item}__{count_dict[item]}")
            else:
                count_dict[item] = 1
                new_list.append(item)
        return new_list

    def getDataFromTable(self, table, useAllColumns = False):
        '''Get the data from the given table with irbank format.
            The table includes 1 column for title, and others are content columns of, each column is differennt year
            In the title columns, each row has its intent and wil be crawled as format:
            A_B_C if A intent < B intent < C intent 
        
            Parameters
            ----------
            table : WebElement
                Table with irbank format
            
            useAllColumns : bool
                If useAllColumns is True, all columns of the table will be extracted,
                else just extract the first and the last column.

            Returns
            -------
            extracted_dfs : list
                List of sub-table dataframes, each dataframe has only two column, the title column, and the content column of only 1 report
        
        '''
        data = []
        
        rows = table.find_elements(By.XPATH, ".//tbody/tr")

        headers = rows[0].find_elements(By.XPATH, ".//th")
        header_range = range(len(headers)) if (len(headers)<=2 or useAllColumns) else range(0, len(headers), 2)
        h = [headers[i].text.replace("\n", " ") for i in header_range]
        data.append(h)
        currency_unit = table.find_element(By.XPATH, ".//caption/span").text.strip()
        if len(header_range) > 1:
            data.append(["Currency"] + [currency_unit for i in range(len(header_range)-1)])
        else:
            data.append(["Currency"])
        indents = [[] for i in range(10)]
        for row in rows[1:]:
            r = []
            cols = row.find_elements(By.XPATH, ".//td")
            for col in cols:
                class_of_col = col.get_attribute("class").split(" ")[0]
                if "indent" in class_of_col:
                    try:
                        number = int(class_of_col[-1])
                    except:
                        number = 0
                        print(f"Something wrong with this indent: {class_of_col}")
                    indents[number].append(col.text.replace("\n", " "))
                    txt = indents[number][-1]
                    number -= 1
                    while number > 0:
                        if len(indents[number]) > 0:
                            txt = indents[number][-1] + "__" + txt
                        number -= 1
                    r.append(txt)
                else:
                    if cols[-1] == col or useAllColumns:
                        r.append(col.text.replace("\n", " "))
            data.append(r)
        columns = data[0]
        data = data[1:]
        data = pd.DataFrame(data, columns=columns)
        data.iloc[:, 0] = self.normalizeSeries(data.iloc[:, 0])

        if len(data.columns) > 2:
            first_column = data.columns[0]
            extracted_dfs = [data[[first_column, column]] for column in data.columns[1:]]
        else:
            extracted_dfs = [data]
        return extracted_dfs[::-1]

    def concatData(self, list_df):
        '''Concatenate all dataframe with irbank format 
        
            Parameters
            ----------
            list_df : list
                List of dataframes

            Returns
            -------
            s : Dataframe
                Dataframe with key is the unique titles from all dataframe in list_df
        
        '''
        ############ SAVE FOR FUTURE #####################
        # s = pd.concat([x.set_index(0) for x in list_df], axis = 1, keys=range(len(list_df)))
        # s.columns = s.columns.map('{0[1]}_{0[0]}'.format)
        # s = s.reset_index()
        # s.columns = s.iloc[0, :]
        # s = s.iloc[1:, :]
        # return s
        ############ SAVE FOR FUTURE #####################

        result_df = list_df[0]
        on_key = result_df.columns[0]
        # Merge the subsequent DataFrames on the 'Title' column one by one
        for i in range(1, len(list_df)):
            result_df = result_df.merge(list_df[i], on=on_key, how='outer')

        return result_df
    
    def getDataFromLink(self, link, useAllColumns=False):
        '''Get data from given document code 

            Parameters
            ----------
            link : str
                Link to crawl

            useAllColumns : bool
                Extract all columns or not

            Returns
            -------
            dt_tables : list of Dataframe
                List of Dataframe, each dataframe has two column, title and year
        
        '''
        dt_tables = []
        report_type = link[-2:]
        try:
            self.driver.get(link)
            table = self.driver.find_element(By.ID, f"c_{report_type}1")
        except Exception as e:
            print(f"============ {link} has no {report_type} data or something wrong with provided link")
            return dt_tables
        dt_tables = self.getDataFromTable(table, useAllColumns)
        return dt_tables
    
    def getData(self, code, by="financial_code", report_type="pl"):
        '''Get data from given code 
        
            Parameters
            ----------
            code : str
                Company code or Financial code

            by : str
                Define type of code

            report_type : str
                Define type of report (profit and loss or balance sheet)
            
            Returns
            -------
            data : Dataframe
                Dataframe with column as list of year, and index as list of title
        
        '''
        self.newDriver()
        if by == "finacial_code":
            company_code = self.getCompanyCode(code)[1]
        elif by == "company_code":
            company_code = code
        else:
            raise "Only valid with financial code or company code"
        
        if report_type not in ("pl", "bs"):
            raise "Only valid with Income Statent or Balance Sheet type"
        
        dfs = []

        try:
            document_codes = self.getValidDocumentCodes(company_code)
        except:
            print(f"============ {company_code} has no {report_type} data")
            return pd.DataFrame()
        
        for i, document_code in tqdm(enumerate(document_codes)):
            print(document_code)
            if by == "finacial_code":
                company_code = self.getCompanyCode(code)[1]
            elif by == "company_code":
                company_code = code
            else:
                raise "Only valid with financial code or company code"
            
            if report_type not in ("pl", "bs"):
                raise "Only valid with Income Statent or Balance Sheet type"
            
            link = self.setDocumentLink(company_code, document_code, report_type)
            dt_tables = self.getDataFromLink(link, i == len(document_codes) - 1)
            dfs.extend(dt_tables)
        try:
            data = self.concatData(dfs)
        except:
            data = pd.DataFrame()
            
        self.closeDriver()
        return data