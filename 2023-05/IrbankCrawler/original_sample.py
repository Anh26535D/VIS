from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import edge
from time import sleep
import csv
import pandas as pd

REPORT_TYPE = "pl"
C_CODE = "E00015"
F_CODE = "1333"

options = edge.options.Options()
options.add_argument("--headless=new")
driver = webdriver.Edge(options=options)

driver.get(f"https://irbank.net/{C_CODE}/reports")
sleep(1)

pl_link = driver.find_element(By.XPATH, "/html/body/div[3]/main/div[2]/div/div/section/div[1]/table/tbody/tr[1]/td[5]/ul/li[2]/a")\
                .get_attribute("href")
driver.get(pl_link)
sleep(1)

if REPORT_TYPE == "bs":
    bs_link = driver.find_element(By.XPATH, "/html/body/div[3]/main/div[2]/div/div/section/dl/dd[3]/ul/li[2]/a").get_attribute("href")
    driver.get(bs_link)
    sleep(1)

table = driver.find_element(By.ID, f"c_{REPORT_TYPE}1")

def get_data(table):
    data = []
    h = []
    rows = table.find_elements(By.XPATH, ".//tbody/tr")
    headers = rows[0].find_elements(By.XPATH, ".//th")
    if len(headers) > 2:
        for header in headers[0::2]:
            value = header.text.replace('\n', ' ')              
            h.append(value)      
    else:
        for header in headers:
            value = header.text.replace('\n', ' ')              
            h.append(value)
    data.append(h)

    mem = []
    prev_check = 0
    for row in rows[1:]:
        r = []
        cols = row.find_elements(By.XPATH, ".//td")
        cls = row.get_attribute('class')
        if cls == 'row3':
            if prev_check == 1:
                mem[-1] = mem[-1] + "__" + cols[0].text.replace('\n', ' ')
            else:
                mem.append(cols[0].text.replace('\n', ' '))
            prev_check = 1
        else:
            prev_check = 0
            value = cols[0].text.replace('\n', ' ')  
            if len(mem)>0:
                value = str(mem[-1]) + "__" + value            
            r.append(value)

            value = cols[-1].text.replace('\n', ' ')            
            r.append(value)
            data.append(r)
    return pd.DataFrame(data)    

def concat_data(dfs):
    v_index_val = []
    h_index_val = []
    for df in dfs:
        for v in df.iloc[:, 0]:
            if v not in v_index_val:
                v_index_val.append(v)
        for v in df.loc[0]:
            if v not in h_index_val:
                h_index_val.append(v)
    h_index_val = h_index_val[1:]
    dict_data = {k: [] for k in v_index_val}
    for df in dfs:
        for k in dict_data.keys():
            temp_df = df.iloc[:, 0]
            if k in temp_df.tolist():
                idx = 0
                for value in temp_df:
                    if value == k:
                        break
                    idx += 1
                dict_data[k].append(df.iloc[idx, -1])
            else:
                dict_data[k].append("")
    return dict_data

dfs = []
data = get_data(table)
dfs.append(data)

while True:
    nav_btns = table.find_element(By.XPATH, ".//caption/ul").find_elements(By.XPATH, ".//li")
    if len(nav_btns) >= 2:
        backward_btn = nav_btns[0]
        try:
            link = backward_btn.find_element(By.XPATH, ".//a").get_attribute("href")
            driver.get(link)
            print(driver.current_url)
            sleep(1)
        except:
            print("DONE !!!")
            break

        table = driver.find_element(By.ID, "c_pl1")
        data = get_data(table)
        dfs.append(data)

data = concat_data(dfs)
driver.quit()
with open(f'data_{F_CODE}_{REPORT_TYPE}.csv', 'w', newline='', encoding='utf-8') as csvfile: 
    csvwriter = csv.writer(csvfile)  
    csvwriter.writerows([[k] + v for k, v in data.items()])