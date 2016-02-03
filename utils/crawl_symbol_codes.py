import urlparse
import re

import requests
from crawler.nseindia.constants.fno_securities import FNO_SECURITIES
from crawler.urls import STOCK_SYMBOL_CODE_URL


def get_symbol_codes():
    symbol_array = []
    errors = []
    for symbol in FNO_SECURITIES:
        try:
            symbol_code = get_code_for_symbol(symbol)
            if symbol_code:
                symbol_array.append({'symbol': symbol, 'code': symbol_code})
            else:
                errors.append(symbol)
                new_symbol = get_new_symbol_from_error_response(symbol)
                symbol_code = get_code_for_symbol(new_symbol)
                symbol_array.append({'symbol': new_symbol, 'code': symbol_code})

            print symbol, symbol_code

        except Exception as e:
            errors.append(symbol)

    print symbol_array
    print errors

def get_code_for_symbol(symbol):
    url = STOCK_SYMBOL_CODE_URL.format(symbol)
    response = requests.get(url)
    parse_result = urlparse.urlparse(response.url)
    query_dict = urlparse.parse_qs(parse_result.query)

    if 'symbolCode' in query_dict.keys():
        symbol = query_dict['symbol'][0]
        symbol_code = query_dict['symbolCode'][0]
        return symbol_code

    return None

def get_new_symbol_from_error_response(symbol):
    url = STOCK_SYMBOL_CODE_URL.format(symbol)
    response = requests.get(url)
    regex = re.compile('live_market\/dynaContent\/live_watch\/option_chain\/optionKeys.jsp\?symbolCode=[0-9]*&symbol=([a-zA-Z0-9]*)')
    match = regex.search(response._content)
    new_symbol =  match.groups()[0]
    return new_symbol





