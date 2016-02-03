from datetime import datetime
import calendar
import math
from dateutil.relativedelta import relativedelta
from utils.options import option_expiry_dates



def get_option_expiry_date(date, expiry_series):
    return option_expiry_dates.get_option_expiry_date(date, expiry_series)
    # last_day_of_the_month = datetime(
    #     day=calendar.monthrange(date.year, date.month)[1],
    #     month=date.month,
    #     year=date.year
    # )
    #
    # expiry = last_day_of_the_month + relativedelta(months=expiry_series)
    #
    # while expiry.weekday() != 3:
    #     expiry = expiry + relativedelta(days=-1)
    #
    # if date <= expiry:
    #     return expiry
    # else:
    #     first_day_of_next_month = last_day_of_the_month + relativedelta(days=1)
    #     return get_option_expiry_date(first_day_of_next_month, expiry_series)



def standard_deviation(stock_price, volatility, days_to_expiry):
    return stock_price * volatility * .01 * math.sqrt(days_to_expiry) / math.sqrt(365)

def get_close_on_expiry(nifty_data, expiry_date):

    expiry_date_string = expiry_date.strftime('%d-%b-%Y')

    close_on_expiry = next((item['close'] for item in nifty_data
                               if item['date'] == expiry_date_string), None)

    while not close_on_expiry:
        expiry_date = expiry_date + datetime.timedelta(days=-1)
        expiry_date_string = expiry_date.strftime('%d-%b-%Y')
        close_on_expiry = next((item['close'] for item in nifty_data
                           if item['date'] == expiry_date_string), None)


    return close_on_expiry