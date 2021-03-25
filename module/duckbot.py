import pandas as pd
import numpy as np
from datetime import datetime, timezone
import os
import ccxt
import asciichartpy

# setup
API_KEY = os.environ.get('API_KEY')
API_SECRET = os.environ.get('API_SECRET')
SUB_ACCOUNT = os.environ.get('SUB_ACCOUNT')
df_path = "./module/duckbot.csv"


def get_current_total_usd():
    global API_KEY
    global API_SECRET
    global SUB_ACCOUNT

    # get balance
    ftx = ccxt.ftx({"apiKey": API_KEY, "secret": API_SECRET, "enableRateLimit": True})
    ftx.headers = {"FTX-SUBACCOUNT": SUB_ACCOUNT} if len(SUB_ACCOUNT) > 0 else {}
    balance = ftx.fetch_balance()

    # sum total usd
    x = [coin['usdValue'] for coin in balance['info']['result']]
    total_usd = np.sum(x)

    return total_usd


# get and append into csv file then save
retry = 3
total_usd = -1
for i in range(0, retry):
    try:
        total_usd = get_current_total_usd()
        break
    except Exception as e:
        # unused
        error_message = "can not get total usd from FTX API, cause of %s" % str(e)

now_utc = datetime.now(timezone.utc)
df = pd.read_csv(df_path)
df.loc[df.shape[0]] = [now_utc, total_usd]
df.to_csv(df_path, index=False)
# fill empty with previous value
df['total_usd'] = df['total_usd'].replace(to_replace=-1, method='ffill')
# plot to ascii graph
df['utc_date'] = df['utc_datetime'].map(lambda s: str(s)[0:10])  # create date column
df = df.groupby('utc_date').nth(0).reset_index()  # group and pick first
df = df.tail(30)  # only last 30 days
total_usds = df['total_usd'].tolist()
dates = df['utc_date'].tolist()


def show_duckbot_text() -> None:
    print("""My crypto trading [duckbot](https://github.com/jojoee/duckbot) performance on [ftx.com](https://ftx.com/#a=13144711)
```
%s
1 tick = 1 day
latest datetime (UTC): %s
latest total usd ($): %.4f
in last 30 records,
  max: %.4f, min: %.4f
  mean: %.4f, std: %.4f
``` 
""" % (
        asciichartpy.plot(total_usds, cfg={
            "min": min(total_usds),
            "max": max(total_usds),
            "height": 12,
        }),
        dates[-1],
        total_usds[-1],
        np.min(total_usds),
        np.max(total_usds),
        np.average(total_usds),
        np.std(total_usds),
    ))
