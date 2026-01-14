import math
import time
import sys
import pytz
import dateutil.parser
from typing import List, Dict
from datetime import datetime
import requests
import requests_cache
import os
import logging

# env
GITHUB_USER = os.environ.get('GH_USER')
GITHUB_TOKEN = os.environ.get('GH_TOKEN')

# constant
tz = "Asia/Bangkok"

# variable
n_commits: List[str] = []
clock_percent_d: Dict[str, float] = {}

# argument parsing
args = sys.argv[1:]
is_dryrun = False
is_debug = False
for arg in args:
    if arg.startswith("--dryrun"):
        is_dryrun = True
    elif arg.startswith("--debug"):
        is_debug = True
    else:
        sys.exit("you are passing invalid argument")

# logger
logging_level = logging.DEBUG if is_debug else logging.INFO
logging.basicConfig(level=logging_level)

# argument parsing
logging.info('argument parsing: data %s', args)

# setup cache
cache_name = 'github_cache'
logging.info("setup local cache: name %s, start" % cache_name)
requests_cache.install_cache(
    cache_name=cache_name,
    backend='sqlite',
    expire_after=60 * 30
)
logging.info("setup local cache: name %s, finish" % cache_name)


# helper
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


def datetime_from_utc_to_local(date_str: str) -> datetime:
    """

    :param date_str:
    :return:
    """

    global tz

    utctime = dateutil.parser.parse(date_str)
    localtime = utctime.astimezone(pytz.timezone(tz))

    return localtime


def local_dates_to_clock_count(dates: List[datetime]) -> [float]:
    """

    :param dates: list of date string in ISO8601 format e.g. "2022-03-17T01:55:45Z"
    :return: array of count following by [morning, day, evening, night]
    """
    evening = 0
    day = 0
    morning = 0
    night = 0

    for date in dates:
        hr_and_min = float(date.strftime('%H.%M'))  # only hr and min

        if 6 < hr_and_min <= 12:
            morning = morning + 1
        elif 12 < hr_and_min <= 18:
            day = day + 1
        elif hr_and_min > 18 or hr_and_min == 0:
            evening = evening + 1
        elif 0 < hr_and_min <= 6:
            night = night + 1
        else:
            logging.info("local_dates_to_clock_count: error")
            sys.exit("local_dates_to_clock_count: error")

    return [morning, day, evening, night]


def show_commit_text() -> None:
    global clock_percent_d
    global n_commits

    print("""Hi :smiley: :wave:   , in the latest %s commits :bug:, am I morning person ?
| | | | |%%|
| --- | --- | --- | --- | --- |
| :sunny: | Morning | (06.00-12.00] | %s | %.2f |
| :satisfied: | Daytime | (12.00-18.00] | %s | %.2f |
| :moon: | Evening | (18.00-00.00] | %s | %.2f |
| :sleeping: | Night | (00.00-06.00] | %s | %.2f |
""" % (
        n_commits,
        percent_to_progressbar(clock_percent_d['morning']), clock_percent_d['morning'],
        percent_to_progressbar(clock_percent_d['day']), clock_percent_d['day'],
        percent_to_progressbar(clock_percent_d['evening']), clock_percent_d['evening'],
        percent_to_progressbar(clock_percent_d['night']), clock_percent_d['night'],
    ))


def proceed() -> None:
    global clock_percent_d
    global n_commits

    # get data and convert to Dict[]
    logging.info("get event data from github: name jojoee, start")
    target_api = "https://api.github.com/users/jojoee/events?per_page=100"
    requests_auth = (GITHUB_USER, GITHUB_TOKEN)
    events = requests.get(target_api, auth=requests_auth).json()
    logging.debug("get event data from github: name jojoee, finish, %s", events)

    # validate API response is a list
    if not isinstance(events, list):
        logging.error("GitHub API returned error: %s", events)
        sys.exit(1)

    # proceed the events - collect commit data from PushEvents using Compare API
    logging.info("get commit data from github: name jojoee, start")
    local_dates: List[datetime] = []
    
    for event in events:
        if not isinstance(event, dict) or event.get("type") != "PushEvent":
            continue
            
        payload = event.get("payload", {})
        repo_name = event.get("repo", {}).get("name", "")
        before_sha = payload.get("before", "")
        head_sha = payload.get("head", "")
        
        if not (repo_name and before_sha and head_sha):
            continue
        
        compare_url = f"https://api.github.com/repos/{repo_name}/compare/{before_sha}...{head_sha}"
        logging.debug("Using compare API: %s", compare_url)
        
        time.sleep(0.2)  # rate limit
        requests_auth = (GITHUB_USER, GITHUB_TOKEN)
        compare_res = requests.get(compare_url, auth=requests_auth).json()
        
        if not isinstance(compare_res, dict):
            logging.warning("Invalid compare response: %s", compare_res)
            continue
        
        for commit in compare_res.get("commits", []):
            try:
                commit_date = commit.get("commit", {}).get("committer", {}).get("date", "")
                if commit_date:
                    local_date = datetime_from_utc_to_local(commit_date)
                    local_dates.append(local_date)
            except (KeyError, TypeError) as e:
                logging.warning("Failed to parse commit date: %s", e)
                continue
    
    logging.info("get commit data from github: name jojoee, finish")

    # print
    n_commits = len(local_dates)
    logging.info("n_commits: %s", n_commits)

    # no new commits then exit (skip commit step in CI)
    if n_commits <= 0:
        logging.info("No new commits found, exiting")
        sys.exit(0)

    # count the clock
    clock_counts = local_dates_to_clock_count(local_dates)
    clock_count_d = {
        "morning": clock_counts[0],
        "day": clock_counts[1],
        "evening": clock_counts[2],
        "night": clock_counts[3],
    }
    logging.info("clock_count_d %s", clock_count_d)

    clock_percent_d = {
        "morning": round(clock_count_d["morning"] / n_commits, 2) * 100,
        "day": round(clock_count_d["day"] / n_commits, 2) * 100,
        "evening": round(clock_count_d["evening"] / n_commits, 2) * 100,
        "night": round(clock_count_d["night"] / n_commits, 2) * 100,
    }


def proceed_dryrun() -> None:
    global n_commits
    global clock_percent_d

    n_commits = 142
    n_morning_commits = 25
    n_day_commits = 30
    n_evening_commits = 20
    n_night_commits = n_commits - n_morning_commits - n_day_commits - n_evening_commits
    clock_percent_d = {
        "morning": n_morning_commits,
        "day": n_day_commits,
        "evening": n_evening_commits,
        "night": n_night_commits
    }


if is_dryrun:
    proceed_dryrun()
else:
    proceed()
