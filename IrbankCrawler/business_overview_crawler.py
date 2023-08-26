import pandas as pd
import requests
from lxml import html
import csv
import sys
import codecs

try:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
except:
    pass

INDUSTRY = '業種'
SEGMENT = 'セグメント'

ROOT_PATH = "E:/vis/vis_repo/2023-06/IrbankCrawler"
LIST_COMPANIES_PATH = ROOT_PATH + "/" + "codes.csv"
companyIDs = pd.read_csv(LIST_COMPANIES_PATH)

data = []
title = ["Symbol", "Industry", "Segment"]
data.append(title)

for symbol, company_code in companyIDs[["fcode", "ccode"]].to_numpy():
    print("-------------", symbol)
    row = [symbol]

    response = requests.get(f"https://irbank.net/{company_code}")
    if response.status_code != 200:
        print(f"Failed to retrieve data for {symbol}")
        continue

    tree = html.fromstring(response.content)
    elements = tree.cssselect(".inline.mgr.wmq")

    if len(elements) < 2:
        print(f"No data in {symbol}")
        continue

    header = elements[1].find(".//h2")
    content_div = elements[1].find('.//dl[@class="sdl"]')

    if content_div is None:
        print(f"No content found for {symbol}")
        continue

    contents = content_div.findall('./*')

    industries = []
    segments = []
    for i, content in enumerate(contents):
        if content.tag == 'dt':
            if content.text_content() == INDUSTRY:
                j = i + 1
                while j < len(contents) and contents[j].tag == 'dd':
                    industries.append(contents[j].text_content())
                    j += 1
            elif content.text_content() == SEGMENT:
                j = i + 1
                while j < len(contents) and contents[j].tag == 'dd':
                    segments.append(contents[j].text_content())
                    j += 1

    row.append(", ".join(industries))
    row.append(", ".join(segments))
    data.append(row)

with open(
    ROOT_PATH + f"/business_overview_data.csv",
    "w",
    newline="",
    encoding="utf-8",
) as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(data)
