import os
import pandas as pd
import csv

import sys
import codecs

try:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
except:
    pass

PATH = "F:/DVA_irbank/Financial"

for doc_type in ("pl", "bs"):
    print(f"START with {doc_type}")
    fields = []
    
    if doc_type == "pl":
        field_path = PATH + "/IncomeStatement"
    elif doc_type == "bs":
        field_path = PATH + "/BalanceSheet"

    for file_name in os.listdir(field_path):
        file_path = field_path + "/" + file_name
        size = os.path.getsize(file_path)
        if size > 0:
            try:
                df = pd.read_csv(file_path).iloc[:, 0].to_list()
                fields = fields + [v for v in df if v not in fields]
            except:
                print(f"Pandas cannot read the file {file_path}")
        else:
            continue
    
    with open(f'{doc_type}_fields.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)  
        csvwriter.writerows([[v] for v in fields])