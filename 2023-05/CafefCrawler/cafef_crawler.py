import sys
import codecs
try:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
except:
    pass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import edge
from time import sleep
import csv

options = edge.options.Options()
options.add_argument("--headless=new")
driver = webdriver.Edge(options=options)

driver.get("https://s.cafef.vn/Lich-su-giao-dich-FRT-1.chn")
sleep(1)

data = []
fields = [
    "Ngày","Giá điều chỉnh","Giá đóng cửa",
    "Thay đổi (+/-%)","GD khớp lệnh - KL","GD khớp lệnh - GT",
    "GD thỏa thuận - KL","GD thỏa thuận - GT",
    "Giá mở cửa","Giá cao nhất","Giá thấp nhất"
]
data.append(fields)

for i in range(20):
    table = driver.find_element(By.ID, "GirdTable2")
    rows = table.find_elements(By.XPATH, ".//tbody/tr")
    for i in range(2, len(rows)):
        r = []
        cols = rows[i].find_elements(By.XPATH, ".//td")
        for col in cols:
            display_property = col.value_of_css_property("display")
            if display_property != "none":
                value = ""
                try:
                    col.find_elements(By.XPATH, "./*")
                    value = col.find_element(By.XPATH, "./*[1]").text.replace('\n', ' ')
                    if value == "":
                        continue
                except:
                    value = col.text.replace('\n', ' ')              
                r.append(value)
        data.append(r)
    try:
        btn = driver.find_element(
            By.XPATH, 
            "/html/body/form/div[3]/div/div[2]/div[2]/div[1]/div[3]/div/div/div[2]/div[2]/div[2]/div/div/div/div/table/tbody/tr/td[last()]/a")
        btn.click()
        sleep(2)
    except:
        break

driver.quit()

with open('data.csv', 'w', newline='', encoding='utf-8') as csvfile: 
    csvwriter = csv.writer(csvfile)  
    csvwriter.writerows(data)