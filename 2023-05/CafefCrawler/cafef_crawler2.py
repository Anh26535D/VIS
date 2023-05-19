import sys
import codecs
try:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
except:
    pass

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver import edge
from time import sleep
import csv
import re

options = edge.options.Options()
options.add_argument("--headless=new")
driver = webdriver.Edge(options=options)

driver.get("https://s.cafef.vn/hose/FRT-cong-ty-co-phan-ban-le-ky-thuat-so-fpt.chn")
sleep(1)

data = []
fields = [
    "Ngày","Cổ phiếu", "Tiền"
]
data.append(fields)

hoverable = driver.find_element(By.XPATH, "/html/body/form/div[3]/div[2]/div[4]/div[2]/div[2]/div[1]/div/div[7]/div[3]/div/div[3]/div")
ActionChains(driver).move_to_element(hoverable).perform()

rows = driver.find_element(
    By.XPATH, 
    "/html/body/form/div[3]/div[2]/div[4]/div[2]/div[2]/div[1]/div/div[7]/div[3]/div/div[3]/div/div/div[2]"
).text.split("\n")

contents = []
prev_idx = -1
for r in rows:
    str = " ".join([v for v in r.split(' ') if v != ""]).lower()
    if str[0] == '-' and ('cổ phiếu' in str or 'tiền' in str):
        contents.append(str[2:])
        prev_idx += 1
    elif str[0] != '-':
        contents[prev_idx] += ' ' + str

data = []
data.append(fields)

for content in contents:
    dividend_pattern = r"(\d{2}/\d{2}/\d{4}):.+?tỷ lệ (\d+:\d+)"
    dividend_matches = re.findall(dividend_pattern,content)

    money_dividend_pattern = r"(\d{2}/\d{2}/\d{4}):.+?tỷ lệ (\d+%)"
    money_dividend_matches = re.findall(money_dividend_pattern,content)

    dividend_dict = {}

    for date, share_rate in dividend_matches:
        dividend_dict[date] = {'Share Rate': share_rate, 'Money Rate': ''}

    for date, money_rate in money_dividend_matches:
        if date not in dividend_dict:
            dividend_dict[date] = {'Share Rate': '', 'Money Rate': money_rate}
        else:
            dividend_dict[date]['Money Rate'] = money_rate

    row = []
    k = list(dividend_dict.keys())[0]
    row.append(k)
    row.append(dividend_dict[k]['Share Rate'])
    row.append(dividend_dict[k]['Money Rate'])
    data.append(row)

with open('data2.csv', 'w', newline='', encoding='utf-8') as csvfile: 
    csvwriter = csv.writer(csvfile)  
    csvwriter.writerows(data)
