import requests as r
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from collections import Counter
from CommonLink import CommonLink
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver import chrome
from selenium.webdriver import edge

class IrbankCrawler:

    def __init__(self, browser="chrome", exe_path=None) -> None:
        self.browser = browser
        self.exe_path = exe_path
        if browser == "edge":
            self.options = edge.options.Options()
            self.options.add_argument("--headless=new")
            self.driver = webdriver.Edge(options=self.options)
        elif browser == "chrome":
            self.options = chrome.options.Options()
            self.options.add_argument("--headless=new")
            
    def newDriver(self):
        if self.browser == "edge":
            self.driver = webdriver.Edge(options=self.options)
        elif self.browser == "chrome":
            self.driver = webdriver.Chrome(options=self.options)

    def closeDriver(self):
        self.driver.close()

    def setDocumentLink(self, company_code, document_code, report_type):
        link = CommonLink.DOCUMENT_LINK
        link = link.replace("company_code", str(company_code))
        link = link.replace("document_code", str(document_code))
        link = link.replace("report_type", str(report_type))
        return link
    
    def setReportLink(self, code):
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
        return series

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
        data = pd.DataFrame(data)
        data.iloc[:, 0] = self.normalizeSeries(data.iloc[:, 0])

        if len(data.columns) > 2:
            first_column = data.columns[0]
            extracted_dfs = [data[[first_column, column]] for column in data.columns[1:]]
        else:
            extracted_dfs = [data]
        return extracted_dfs[::-1]

    def concat_data(self, dfs):
        '''Concatenate all dataframe with irbank format 
        
            Parameters
            ----------
            dfs : list
                List of dataframes

            Returns
            -------
            dict_data : dictionary
                Dictionary with key is the unique titles from all dataframe in dfs
        
        '''
        v_index_val = []
        for df in dfs:
            for v in df.iloc[:, 0]:
                if v not in v_index_val:
                    v_index_val.append(v)

        dict_data = {k: [] for k in v_index_val}

        for df in dfs:
            for k in v_index_val:
                index_column = df.iloc[:, 0]
                if k in index_column.tolist():
                    idx = index_column[index_column == k].index[0]
                    dict_data[k].append(df.iloc[idx, -1])
                else:
                    dict_data[k].append("")

        return dict_data
    
    def getDataFromDocumentCode(self, document_code, code, by="financial_code", report_type="pl", useAllColumns=False):
        if by == "finacial_code":
            company_code = self.getCompanyCode(code)[1]
        elif by == "company_code":
            company_code = code
        else:
            raise "Only valid with financial code or company code"
        
        if report_type not in ("pl", "bs"):
            raise "Only valid with Income Statent or Balance Sheet type"
        
        link = self.setDocumentLink(company_code, document_code, report_type)
        dt_tables = []
        try:
            self.driver.get(link)
            table = self.driver.find_element(By.ID, f"c_{report_type}1")
        except:
            print(f"============ {document_code} has no {report_type} data")
            return dt_tables
        dt_tables = self.getDataFromTable(table, useAllColumns)
        return dt_tables
    
    def getData(self, code, by="financial_code", report_type="pl"):
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
        data = {}

        try:
            document_codes = self.getValidDocumentCodes(company_code)
        except:
            print(f"============ {company_code} has no {report_type} data")
            return data
        
        for i in tqdm(range(len(document_codes))):
            dt_tables = self.getDataFromDocumentCode(
                            document_codes[i],
                            company_code,
                            by="company_code",
                            report_type=report_type,
                            useAllColumns=(i == len(document_codes) - 1)
                        )
            dfs.extend(dt_tables)
        data = self.concat_data(dfs)
        self.closeDriver()
        return data
