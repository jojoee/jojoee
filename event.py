import json
import urllib.request
from datetime import datetime
import math
import time
import sys


def datetime_from_utc_to_local(utc_datetime: datetime):
    """

    :param utc_datetime:
    :return:
    """
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


def percent_to_progressbar(percent: float):
    """

    :param percent: percent percentage 53.36
    :return:
    """
    bar_length = 20
    percent = percent

    n_items = math.floor(percent / 100 * bar_length)
    n_spaces = bar_length - n_items

    return "[%s%s]" % (n_items * "*", n_spaces * "-")


# get data and convert to Dict[]
target_api = "https://api.github.com/users/jojoee/events?per_page=100"
res_bytes = urllib.request.urlopen(target_api).read()
res_str = res_bytes.decode("utf-8")
events = json.loads(res_str)

# proceed
event_type_d = {}
clock_count_d = {
    "morning": 0,
    "day": 0,
    "evening": 0,
    "night": 0,
}
for event in events:
    # count event types
    event_type = event["type"]
    if event_type not in event_type_d:
        event_type_d[event_type] = 0
    event_type_d[event_type] = event_type_d[event_type] + 1

    # count commit event
    if event_type == "PushEvent":
        date_str = event['created_at']  # e.g. '2020-10-02T10:05:24Z'
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')  # str to datetime
        local_date = datetime_from_utc_to_local(date)  # local date
        hr_and_min = float(local_date.strftime('%H.%M'))  # only hr and min

        if hr_and_min > 18:
            clock_count_d["evening"] = clock_count_d["evening"] + 1
        elif hr_and_min > 12:
            clock_count_d["day"] = clock_count_d["day"] + 1
        elif hr_and_min > 6:
            clock_count_d["morning"] = clock_count_d["morning"] + 1
        elif hr_and_min > 0:
            clock_count_d["night"] = clock_count_d["night"] + 1
        else:
            sys.exit("something went wrong")

n_push_events = event_type_d["PushEvent"]
clock_percent_d = {
    "morning": round(clock_count_d["morning"] / n_push_events, 2) * 100,
    "day": round(clock_count_d["day"] / n_push_events, 2) * 100,
    "evening": round(clock_count_d["evening"] / n_push_events, 2) * 100,
    "night": round(clock_count_d["night"] / n_push_events, 2) * 100,
}

print("""Hi :smiley: :wave:

[![Visits Badge](https://badges.pufler.dev/visits/jojoee/jojoee)](https://github.com/jojoee/jojoee)<img src="https://jojoee.jojoee.com/api/utcnow" width="120" height="20">

In the latest %s commits :bug:, am I morning person ? 
| | | | |%%|
| --- | --- | --- | --- | --- |
| :sunny: | Morning | (06.00-12.00] | %s | %.0f |
| :satisfied: | Daytime | (12.00-18.00] | %s | %.2f |
| :moon: | Evening | (18.00-00.00] | %s | %.2f |
| :sleeping: | Night | (00.00-06.00] | %s | %.2f |

<img src="https://github-readme-stats.vercel.app/api/top-langs/?username=jojoee&layout=compact" />
""" % (
    n_push_events,
    percent_to_progressbar(clock_percent_d['morning']), clock_percent_d['morning'],
    percent_to_progressbar(clock_percent_d['day']), clock_percent_d['day'],
    percent_to_progressbar(clock_percent_d['evening']), clock_percent_d['evening'],
    percent_to_progressbar(clock_percent_d['night']), clock_percent_d['night'],
))
