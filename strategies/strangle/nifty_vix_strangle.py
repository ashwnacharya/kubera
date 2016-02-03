import json
from utils.options.option_utils import get_option_expiry_date, standard_deviation
import datetime
import math
from os import path

def check_strangle_profitability():
    nifty_data = None
    vix_data = None

    with open('nifty.json') as data_file:
        nifty_data = json.load(data_file)


    with open('vix.json') as data_file:
        vix_data = json.load(data_file)


    results = []


    for nifty_entry in nifty_data:
        entry_date = datetime.datetime.strptime(nifty_entry['date'], '%d-%b-%Y')

        volatility = next((item['close'] for item in vix_data if item['date'] == nifty_entry['date']), None)
        if not volatility:
            continue

        expiry_date = get_option_expiry_date(entry_date, 0)
        expiry_date_string = expiry_date.strftime('%d-%b-%Y')
        close_on_expiry = next((item['close'] for item in nifty_data
                               if item['date'] == expiry_date_string), None)

        while not close_on_expiry:
            expiry_date = expiry_date + datetime.timedelta(days=-1)
            expiry_date_string = expiry_date.strftime('%d-%b-%Y')
            close_on_expiry = next((item['close'] for item in nifty_data
                               if item['date'] == expiry_date_string), None)


        days_to_expiry = (expiry_date-entry_date).days

        deviation = standard_deviation(stock_price=nifty_entry['close'],
                                       volatility=volatility,
                                       days_to_expiry=days_to_expiry
                                       ) if days_to_expiry > 0 else 0


        invest = False

        if deviation/nifty_entry['close'] > .05:
            invest = True

        put_strike = math.floor((nifty_entry['close'] - deviation)/100)*100
        call_strike = math.ceil((nifty_entry['close'] + deviation)/100)*100
        put_premium = get_premium(entry_date, put_strike, 'PE')
        call_premium = get_premium(entry_date, call_strike, 'CE')
        total_premium = put_premium + call_premium

        profit = close_on_expiry > put_strike and close_on_expiry < call_strike

        loss = 0

        if not profit:
            if close_on_expiry < put_strike:
                loss = put_strike-close_on_expiry - total_premium
            else:
                loss = close_on_expiry-call_strike - total_premium




        result = {
            'date': nifty_entry['date'],
            'price': nifty_entry['close'],
            'volatility': volatility,
            'deviation': deviation,
            'expiry_date': expiry_date_string,
            'days_to_expiry': days_to_expiry,
            'invest': invest,
            'close_on_expiry': close_on_expiry,
            'put_strike': put_strike,
            'call_strike': call_strike,
            'put_premium': put_premium,
            'call_premium': call_premium,
            'total_premium': total_premium,
            'profit': profit,
            'loss': loss
        }

        results.append(result)

    with open('nifty_strangle.json', 'w') as the_file:
        the_file.write(json.dumps(results))

    with open('nifty_strangle.csv', 'w') as the_file:
        for result in results:
            the_file.write('{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(
                result['date'],
                result['price'],
                result['volatility'],
                result['deviation'],
                result['expiry_date'],
                result['days_to_expiry'],
                result['invest'],
                result['close_on_expiry'],
                result['put_strike'],
                result['call_strike'],
                result['put_premium'],
                result['call_premium'],
                result['total_premium'],
                result['profit'],
                result['loss']
            ))


def get_premium(date, strike, option_type):
    file_name = date.strftime('%d-%m-%Y')
    file_name = 'nifty_option_chain/' + file_name + '.json'

    file_path = path.abspath(file_name)

    option_chain_data = None
    with open(file_path) as data_file:
        option_chain_data = json.load(data_file)

    i = 0
    if option_type == 'PE':
        i = 1

    entry = [item for item in option_chain_data[i] if item['strike_price'] == strike]

    if entry:
        print 'Found option price {} {} {}'.format(date, strike, option_type)
        return entry[0]['close']
    else:
        print 'Cannot find option price {} {} {}'.format(date, strike, option_type)
        return 0


