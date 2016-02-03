import requests
import datetime
import json
import time

# Start Date and End date format in dd-mmm-yyyy with date range not more than 365 days.
# Eg: 'http://www.nseindia.com/content/vix/histdata/hist_india_vix_01-Nov-2015_30-Nov-2015.csv'
_HISTORICAL_DATA_CSV_URL = 'http://www.nseindia.com/content/vix/histdata/hist_india_vix_{}_{}.csv'

HISTORICAL_DATA_CSV_COLUMNS = [
    'DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'PREV_CLOSE', 'CHANGE', 'PERCENT_CHANGE'
]

RANGE_UNITS = 'days'

RANGE_DELTA = 365


def crawl(start_date, end_date):
    start_date_string = start_date.strftime('%d-%b-%Y')
    end_date_string = end_date.strftime('%d-%b-%Y')
    url = _HISTORICAL_DATA_CSV_URL.format(start_date_string, end_date_string)
    response = requests.get(url)
    print url
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
                'prev_close': float(item[5].strip()),
                'change': float(item[6].strip()),
                'percent_change': float(item[7].strip()),
            }

            data.append(entry)

    return data

def get_all_data():
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

    with open('vix.json', 'w') as the_file:
        the_file.write(json.dumps(all_data))

    print all_data