import requests
import csv
import collections
import time
from decimal import Decimal
import json
import datetime
from crawler import crawler_settings


# Start Date and End date format in dd-mm-yyyy with date range not more than 365 days.
# Eg: 'http://www.nseindia.com/content/indices/histdata/CNX NIFTY01-01-2015-01-11-2015.csv'

CSV_URL = \
    'http://www.nseindia.com/content/indices/histdata/CNX NIFTY{}-{}.csv'

_CSV_COLUMNS = [
    "DATE", "OPEN", "HIGH", "LOW", "CLOSE", "SHARES", "TURNOVER"
]

RANGE_UNITS = 'days'

RANGE_DELTA = 365

def crawl(start_date, end_date):
    start_date_string = start_date.strftime('%d-%m-%Y')
    end_date_string = end_date.strftime('%d-%m-%Y')
    url = CSV_URL.format(start_date_string, end_date_string)
    print url
    response = requests.get(url)
    return response._content

def parse(content):
    string_arrays = content.split('\n')
    string_arrays.pop(0)

    data = []

    for string_entry in string_arrays:
        if string_entry:
            item = string_entry.replace('"', '').split(',')

            entry = {
                'date': item[0].strip(),
                'open': float(item[1].strip()),
                'high': float(item[2].strip()),
                'low': float(item[3].strip()),
                'close': float(item[4].strip()),
                'shares': float(item[5].strip()),
                'turnover': float(item[6].strip())
            }

            data.append(entry)

    return data


def get_all_data():
    # start_date = crawler_settings.CRAWLER_START_DATE
    # timedelta_args = {RANGE_UNITS: RANGE_DELTA}
    # end_date = start_date + timedelta(**timedelta_args)

    year = 2010
    start_date = datetime.datetime(day=1, month=1, year=year)
    end_date = datetime.datetime(day=31, month=12, year=year)

    all_data = []

    while start_date < datetime.datetime.now():
        crawled_data = crawl(start_date=start_date, end_date=end_date)
        parsed_data = parse(crawled_data)
        all_data = all_data + parsed_data

        time.sleep(15)

        year = year+1
        start_date = datetime.datetime(day=1, month=1, year=year)
        end_date = datetime.datetime(day=31, month=12, year=year)

    import ipdb; ipdb.set_trace()

    with open('somefile.txt', 'w') as the_file:
        the_file.write(json.dumps(all_data))

    print all_data
