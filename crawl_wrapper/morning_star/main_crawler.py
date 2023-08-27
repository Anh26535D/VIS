from MorningStarCrawler import MorningStarCrawler
import os
import pandas as pd

base_path = r"E:\vis\vis_repo\crawl_wrapper\morning_star"
list_symbols_path = os.path.join(base_path, "list_companies.csv")
save_path = os.path.join(base_path, "price_data")
log_path = os.path.join(base_path, "error_symbols.txt")

symbols = pd.read_csv(list_symbols_path).values.flatten(order="F")
symbols = symbols[pd.notna(symbols)]
num_symbols = len(symbols)

crawler = MorningStarCrawler()


for i, symbol in enumerate(symbols):
    print(f"====> {i}/{num_symbols} ===> start with {symbol}", end=" ")

    price_data, log_error = crawler.getPriceData(symbol=symbol, timeout=500)

    if log_error == "OK":
        print(f"===> Sucessfully. {price_data.shape}")
        save_file_path = os.path.join(save_path, f"{symbol}.csv")
        price_data.to_csv(save_file_path, index=False)
    else: 
        print(f"===> Unsuccessfully. {log_error}")
        with open(log_path, mode="a") as log_file:
            log_file.write(f"{symbol} has {log_error}\n")
