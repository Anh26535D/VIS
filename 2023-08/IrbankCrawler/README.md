## Temporary Note
- Methods were commented in IrbankCrawler

File name  | Function
------------- | -------------
IrbankCrawler.py  | use getCompanyCode to get all symbol's code first
link_main_crawler.py  | get all possible pl (bs) link of a code (from above result)
IrbankCrawler.py  | use getData with links crawled in above file

## Quick guide
```rb
from IrbankCrawler import IrbankCrawler
import pandas as pd

1. Run this to obtain symbol_code file (each row is pair (symbol, code))
df = pd.read_csv("symbol.csv")
df["Code"] = df["Symbol"].apply(IrbankCrawler.getCompanyCode)
df.to_csv("symbol_code.csv", index=False)

2. Run file link_main_crawler.py (remember to correct paths)

3. Use getData from IrbankCrawler.py for crawling (remember to correct paths)
-----(optional) you can also use crawl_extra.py if you like (remember to correct paths)
```
