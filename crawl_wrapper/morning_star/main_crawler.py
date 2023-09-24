from MorningStarCrawler import MorningStarCrawler
import os
import pandas as pd

IGNORE_FLAG = True

base_path = r"E:\vis\vis_repo\crawl_wrapper\morning_star"
list_symbols_path = os.path.join(base_path, "security_id.csv")
save_path = os.path.join(base_path, "financial", "IncomeStatement")
log_path = os.path.join(base_path, "error_symbols.txt")
log_file_path = os.path.join(base_path, "edge-net-export-log.json")

df = pd.read_csv(list_symbols_path)
data = {}
for index, row in df.iterrows():
    key = row['Symbol']
    sub_dict = {'Security_id': row['Security_id'], 'Error_code': row['Error_code']}
    data[key] = sub_dict

crawler = MorningStarCrawler()

if IGNORE_FLAG:
    crawled_symbols = [symbol.split(".")[0] for symbol in os.listdir(save_path)]
    symbols = [symbol for symbol in data.keys() if symbol not in crawled_symbols]
num_symbols = len(symbols)

for i, symbol in enumerate(symbols):
    print(f"====> {i}/{num_symbols} ===> start with {symbol}", end=" ")

    data, error_code = crawler.getDividendAndSplitDataFromAPI(symbol, security_id=data[symbol]["Security_id"])
    if error_code == 101:
        if crawler.resetBearerToken(log_file_path=log_file_path, wait_time=5):
            data, error_code = crawler.getDividendAndSplitDataFromAPI(symbol, security_id=data[symbol]["Security_id"])
    elif error_code != 100:
        with open(log_path, "a") as f:
            f.write(f"{symbol}\n")
    print(error_code)