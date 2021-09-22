import pandas as pd
import numpy as np
from datetime import datetime, timezone
import os
import ccxt
import asciichartpy
from typing import List
from dataclasses import dataclass


@dataclass
class FtxBot:
    sub_account: str
    api_key: str
    api_secret: str


def get_total_usd(sub_account: str, api_key: str, api_secret: str) -> float:
    # get balance
    ftx = ccxt.ftx({"apiKey": api_key, "secret": api_secret, "enableRateLimit": True})
    ftx.headers = {"FTX-SUBACCOUNT": sub_account} if len(sub_account) > 0 else {}
    balance = ftx.fetch_balance()

    # total usd
    total_usd = np.sum([coin["usdValue"] for coin in balance["info"]["result"]])

    return total_usd


# setup
ftx_bots = [
    FtxBot(
        os.environ.get('SUB_ACCOUNT'),
        os.environ.get('API_KEY'),
        os.environ.get('API_SECRET'),
    ),
    FtxBot(
        os.environ.get('SUB_ACCOUNT2'),
        os.environ.get('API_KEY2'),
        os.environ.get('API_SECRET2'),
    ),
    FtxBot(
        os.environ.get('SUB_ACCOUNT3'),
        os.environ.get('API_KEY3'),
        os.environ.get('API_SECRET3'),
    )
]
bot_names = [bot.sub_account for bot in ftx_bots]
df_path = "./module/duckbot.csv"

# get data
total_usds = [get_total_usd(bot.sub_account, bot.api_key, bot.api_secret) for bot in ftx_bots]

# format
now_utc = datetime.now(timezone.utc)
df = pd.read_csv(df_path)
df.loc[df.shape[0]] = [now_utc] + total_usds  # append to the last
df.to_csv(df_path, index=False)

# plot to ascii graph
n_displayed_days = 90
df["utc_date"] = df["utc_datetime"].map(lambda s: str(s)[0:10])  # create date column
df = df.groupby("utc_date").nth(0).reset_index()  # group and pick first
df = df.tail(n_displayed_days)  # only last 30 days
n_displayed_days = min(df.shape[0], n_displayed_days)


def show_duckbot_text() -> None:
    global df

    dates = df["utc_date"].tolist()
    data = [df["%s_total_usd" % name].tolist() for name in bot_names]
    flatten_data = np.array(data).flatten()
    print("""My crypto trading [duckbot](https://github.com/jojoee/duckbot) performance on [ftx.com](https://ftx.com/#a=13144711)
```
%s
```
Most recent %d days of portfolio, 1 tick = 1 day<br />
Last check date (UTC+0): %s
- duckbot001 total usd: %.4f$ (rebalance [DOGEBULL/USD](https://ftx.com/trade/DOGEBULL/USD#a=13144711) 50:50)
- duckbot002 total usd: %.4f$ (rebalance [BNBBULL/USD](https://ftx.com/trade/BNBBULL/USD#a=13144711) 50:50)
- duckbot003 total usd: %.4f$ (rebalance [BULL/USD](https://ftx.com/trade/BULL/USD#a=13144711) 50:50)
""" % (
        asciichartpy.plot(data, cfg={
            "min": min(flatten_data),
            "max": max(flatten_data),
            "height": 16,
        }),
        n_displayed_days,
        dates[-1],
        df["duckbot001_total_usd"].tolist()[-1],
        df["duckbot002_total_usd"].tolist()[-1],
        df["duckbot003_total_usd"].tolist()[-1]
    ))
