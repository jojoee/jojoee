import pandas as pd
import numpy as np
from datetime import datetime, timezone
import os
import ccxt
import asciichartpy
from typing import List

# setup
API_KEY = os.environ.get('API_KEY')
API_SECRET = os.environ.get('API_SECRET')
SUB_ACCOUNT = os.environ.get('SUB_ACCOUNT')
df_path = "./module/duckbot.csv"

# get and append into csv file then save
retry = 3
usd = -1
total_usd = -1
coins: List[str] = []
for i in range(0, retry):
    try:
        # get balance
        ftx = ccxt.ftx({"apiKey": API_KEY, "secret": API_SECRET, "enableRateLimit": True})
        ftx.headers = {"FTX-SUBACCOUNT": SUB_ACCOUNT} if len(SUB_ACCOUNT) > 0 else {}
        balance = ftx.fetch_balance()

        # usd
        usd = balance['USD']['total']

        # total usd
        total_usd = np.sum([coin['usdValue'] for coin in balance['info']['result']])

        # coin list
        coins = [result['coin'] for result in balance['info']['result']]

        break
    except Exception as e:
        # unused
        error_message = "can not get total usd from FTX API, cause of %s" % str(e)

now_utc = datetime.now(timezone.utc)
df = pd.read_csv(df_path)
df.loc[df.shape[0]] = [now_utc, usd, total_usd]
df.to_csv(df_path, index=False)
# fill empty with previous value
df['total_usd'] = df['total_usd'].replace(to_replace=-1, method='ffill')
# plot to ascii graph
df['utc_date'] = df['utc_datetime'].map(lambda s: str(s)[0:10])  # create date column
df = df.groupby('utc_date').nth(0).reset_index()  # group and pick first
df = df.tail(30)  # only last 30 days


def show_duckbot_text() -> None:
    global df

    total_usds = df['total_usd'].tolist()
    usds = df['usd'].tolist()
    dates = df['utc_date'].tolist()
    data = [usds, total_usds]
    flatten_data = np.array(data).flatten()
    print("""My crypto trading [duckbot](https://github.com/jojoee/duckbot) performance on [ftx.com](https://ftx.com/#a=13144711)
```
%s
1 tick = 1 day
latest datetime (UTC+0): %s
latest USD ($): %.4f
latest total USD (%s) ($): %.4f
in last 30 records,
  max: %.4f, min: %.4f
  mean: %.4f, std: %.4f
``` 
""" % (
        asciichartpy.plot(data, cfg={
            "min": min(flatten_data),
            "max": max(flatten_data),
            "height": 12,
        }),
        dates[-1],
        usds[-1],
        ' + '.join(map(str, coins)),
        total_usds[-1],
        np.min(total_usds),
        np.max(total_usds),
        np.average(total_usds),
        np.std(total_usds),
    ))
