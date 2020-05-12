from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, timedelta
from django.utils import timezone
import requests
from website.models import Trade_BTC_small, Trade_BTC_medium, Trade_BTC_large, Trade_BTC_test

################################################################################

# default settings
test = True
deltaDays = 7
trades = {}
mode = 0
compareRate = None

################################################################################

class Command(BaseCommand):
    def add_arguments(self, parser):
# Positional arguments
        parser.add_argument('mode', type=int)

    def handle(self, *args, **options):
        global test, deltaDays, trades, mode, compareRate
        if(options['mode'] == 1):
            test = False
            deltaDays = 1
            trades = Trade_BTC_small.objects.order_by('time')
            mode = 1
            print('Settings are: productive on small')
        elif(options['mode'] == 2):
            test = False
            deltaDays = 7
            trades = Trade_BTC_medium.objects.order_by('time')
            mode = 2
            print('Settings are: productive on medium')
        elif(options['mode'] == 3):
            test = False
            deltaDays = 14
            trades = Trade_BTC_large.objects.order_by('time')
            mode = 3
            print('Settings are: productive on large')
        elif(options['mode'] == 0):
            test = True
            deltaDays = 1
            trades = Trade_BTC_test.objects.order_by('time')
            mode = 0
            print('Settings are: test on small')

        jasonValue = request_basic(self)

        if('status_code' not in jasonValue):
            #print(jasonValue)
            lastTrade = trades.last()
#sets the compare rate
            print('check last entry in database')
            if(lastTrade is None):
                compareRate = reset_trade(self, 'nothing in DB', jasonValue)
            elif(lastTrade.time <= (timezone.now()- timedelta(days=deltaDays))):
                compareRate = reset_trade(self, 'too old', jasonValue)
            else:
                print('continue')
                compareRate = lastTrade.rate
            print(compareRate)

        else:
            print('status_code ' + jasonValue['status_code'])

################################################################################

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

################################################################################

def request_basic(self,):
    #rate_url_bitcoin = 'https://api.bitcoin.de/v4/:trading_pair/basic/rate.json?apikey='
    #f = open('C:/Users/Richi/Documents/CollectingDove/CollectingDove/website/apikey_basic.private')
    #privateKey = f.read()
    rate_url_coindesk = 'https://api.coindesk.com/v1/bpi/currentprice.json'
    r = {}

    response = requests.get(rate_url_coindesk)

    if(response.status_code == 200):
        r['time'] = utc_to_local(datetime.strptime(response.json()['time']['updated'][0:21], '%B %d, %Y %H:%M:%S')).strftime('%Y-%m-%d %H:%M:%S')
        r['rate'] = response.json()['bpi']['EUR']['rate_float']
    else:
        r['status_code'] = response.status_code
    return(r)

################################################################################

def reset_trade(self, reason, jsonValue):
    global models
    print('reset, ' + reason)
    if(mode == 0):
        t = Trade_BTC_test(rate=jsonValue['rate'])
    elif(mode == 1):
        t = Trade_BTC_small(rate=jsonValue['rate'])
    elif(mode == 2):
        t = Trade_BTC_medium(rate=jsonValue['rate'])
    elif(mode == 3):
        t = Trade_BTC_large(rate=jsonValue['rate'])
    t.save()
    return(jsonValue['rate'])



################################################################################
