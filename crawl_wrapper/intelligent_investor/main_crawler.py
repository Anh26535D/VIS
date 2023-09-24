from IntelligentInvestorCrawler import IntelligentInvestorCrawler
import os
import pandas as pd

IGNORE_FLAG = True

base_path = r"E:\vis\vis_repo\crawl_wrapper\intelligent_investor"
list_symbols_path = os.path.join(base_path, "list_companies.csv")
save_path = os.path.join(base_path, "price_data")
log_path = os.path.join(base_path, "error_symbols.txt")

symbols = pd.read_csv(list_symbols_path).values.flatten(order="F")
symbols = symbols[pd.notna(symbols)].tolist()

crawler = IntelligentInvestorCrawler()

if IGNORE_FLAG:
    crawled_symbols = [symbol.split(".")[0] for symbol in os.listdir(save_path)]
    symbols = [symbol for symbol in symbols if symbol not in crawled_symbols]
num_symbols = len(symbols)

for i, symbol in enumerate(symbols):
    print(f"====> {i}/{num_symbols} ===> start with {symbol}", end=" ")
    price_data, log_error = crawler.getPriceData(symbol=symbol)
    if log_error == "OK":
        print("===> Sucessfully !!!")
        save_file_path = os.path.join(save_path, f"{symbol}.csv")
        price_data.to_csv(save_file_path, index=False)
    else: 
        print(f"===> Unsuccessfully. {log_error}")
        with open(log_path, mode="a") as log_file:
            log_file.write(f"{symbol} has {log_error}\n")
