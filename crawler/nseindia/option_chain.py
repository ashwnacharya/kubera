import json
import requests
import os
import re
import datetime
import time
import math
import thread
from crawler import crawler_settings
from utils.options.option_utils import get_option_expiry_date, \
    get_close_on_expiry

INTERMEDIATE_URL = \
    'http://www.nseindia.com/products/dynaContent/derivatives/equities/histcontract.jsp?' \
    'symbolCode={}&' \
    'symbol={}&' \
    'instrumentType={}&' \
    'expiryDate={}&' \
    'optionType={}&' \
    'fromDate={}&' \
    'toDate={}&strikePrice='

_CSV_COLUMNS = [
    "SYMBOL", "DATE", "EXPIRY", "OPTION_TYPE", "STRIKE_PRICE", "OPEN", "HIGH",
    "LOW", "CLOSE", "LTP", "SETTLE_PRICE", "NO_OF_CONTRACTS", "TURNOVER",
    "PREMIUM_TURNOVER", "OPEN_INTEREST", "CHANGE_IN_OI", "UNDERLYING_VALUE"
]


def crawl(symbol_code, symbol, instrument_type, expiry_date, option_type, from_date):

    intermediate_url_regex = \
        '<span class="download-data-link">' \
        '<a style="" target="_blank" href="(?P<url>[a-zA-Z0-9.\/_-]*)"'

    expiry_date_string = expiry_date.strftime('%d-%m-%Y')
    from_date_string = from_date.strftime('%d-%b-%Y')
    to_date_string = from_date.strftime('%d-%b-%Y')

    intermediate_url = INTERMEDIATE_URL.format(
        symbol_code,  symbol, instrument_type, expiry_date_string, option_type,
        from_date_string, to_date_string)

    intermediate_response = requests.get(intermediate_url)
    # regex = re.compile(intermediate_url_regex)
    # match = regex.search(intermediate_response._content)
    # csv_url = 'http://www.nseindia.com' + match.group('url')
    # print csv_url
    # csv_response = requests.get(csv_url, cookies=intermediate_response.cookies)
    #
    # time.sleep(60)
    # return csv_response._content

    regex = re.compile('<td class="number">(?P<number>[0-9.,-]*)<\/td>')
    matches = regex.findall(intermediate_response._content)

    chunked = chunks(matches, 13)

    data = []
    for chunk in chunked:
        entry = {
                'symbol': symbol,
                'date': from_date_string,
                'expiry': expiry_date_string,
                'option_type': option_type,
                'strike_price': float(chunk[0].strip().replace(',','').replace('-', '0')),
                'open': float(chunk[1].strip().replace(',','').replace('-', '0')),
                'high': float(chunk[2].strip().replace(',','').replace('-', '0')),
                'low': float(chunk[3].strip().replace(',','').replace('-', '0')),
                'close': float(chunk[4].strip().replace(',','').replace('-', '0')),
                'ltp': float(chunk[5].strip().replace(',','').replace('-', '0')),
                'settle_price': float(chunk[6].strip().replace(',','').replace('-', '0')),
                'no_of_contracts': float(chunk[7].strip().replace(',','').replace('-', '0')),
                'turnover': float(chunk[8].strip().replace(',','').replace('-', '0')),
                'premium_turnover': float(chunk[9].strip().replace('-', '0').replace(',','')),
                'open_interest': float(chunk[10].strip().replace(',','').replace('-', '0')),
                'change_in_oi': float(chunk[11].strip().replace(',','').replace('-', '0')),
                'underlying_value': float(chunk[12].strip().replace(',','').replace('-', '0'))
            }

        data.append(entry)

    return data

def chunks(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]

# def parse(content):
#     string_arrays = content.split('\n')
#     string_arrays.pop(0)
#
#     data = []
#
#     for string_entry in string_arrays:
#         if string_entry:
#             print string_entry
#             item = string_entry.replace('"', '').split(',')
#
#             entry = {
#                 'symbol': item[0].strip(),
#                 'date': item[1].strip(),
#                 'expiry': item[2].strip(),
#                 'option_type': item[3].strip(),
#                 'strike_price': int(item[4].strip()),
#                 'open': float(item[5].strip()),
#                 'high': float(item[6].strip()),
#                 'low': float(item[7].strip()),
#                 'close': float(item[8].strip()),
#                 'ltp': float(item[9].strip()),
#                 'settle_price': float(item[10].strip()),
#                 'no_of_contracts': float(item[11].strip()),
#                 'turnover': float(item[12].strip()),
#                 'premium_turnover': float(item[13].strip().replace('-', '0')),
#                 'open_interest': float(item[14].strip()),
#                 'change_in_oi': float(item[15].strip()),
#                 'underlying_value': float(item[16].strip())
#             }
#
#             data.append(entry)
#
#     return data

def get_strike_prices(nifty_data, expiry_date):
    close_on_expiry = get_close_on_expiry(nifty_data=nifty_data,
                                          expiry_date=expiry_date)

    lower = int(math.floor(close_on_expiry *.85/100))
    upper = int(math.ceil(close_on_expiry*1.15/100))
    return [num*100 for num in range(lower,upper)]


def get_all_data():
    nifty_data = None

    with open('nifty.json') as data_file:
        nifty_data = json.load(data_file)

    expiry_date = datetime.datetime(day=28, month=2, year=2013)
    from_date = datetime.datetime(day=4, month=2, year=2013)

    while from_date < datetime.datetime.now():
        print from_date.strftime('%d-%b-%Y')
        get_data_for_date(expiry_date, from_date, nifty_data)

        from_date = from_date + datetime.timedelta(days=1)

        if from_date > expiry_date:
            expiry_date = get_option_expiry_date(date=from_date,
                                                 expiry_series=0)


def get_data_for_date(expiry_date, from_date, nifty_data):
    nifty_entry = next((item for item in nifty_data
                        if item['date'] == from_date.strftime('%d-%b-%Y')),
                       None)

    if not nifty_entry:
        print 'no nifty entry. exiting'
        return

    parsed_data = crawl_for_date(expiry_date, from_date)
    print parsed_data

    file_name = 'nifty_option_chain/' + from_date.strftime('%d-%m-%Y') + '.json'

    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))

    with open(file_name, 'w') as the_file:
        the_file.write(json.dumps(parsed_data))


def crawl_for_date(expiry_date, from_date):
    data = []
    crawled_data = crawl(symbol='NIFTY', symbol_code=-10007,
                         instrument_type='OPTIDX',
                         expiry_date=expiry_date,
                         from_date=from_date,
                         option_type='CE'
                         )

    data.append(crawled_data)

    crawled_data = crawl(symbol='NIFTY', symbol_code=-10007,
                         instrument_type='OPTIDX',
                         expiry_date=expiry_date,
                         from_date=from_date,
                         option_type='PE'
                         )

    data.append(crawled_data)

    return data
