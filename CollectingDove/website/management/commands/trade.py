from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, timedelta
from django.utils import timezone, dateformat
import requests
from website.models import Trade_BTC_small, Trade_BTC_medium, Trade_BTC_large, Trade_BTC_test, Total_Value, Total_Value_Test, StopTrade
import random

################################################################################

# default settings
test = True
deltaDays = 7
compareDeltaRate = 0
trades = {}
mode = 0
debug = True
debugText = ''
#compareRate = None

################################################################################

class Command(BaseCommand):
    def add_arguments(self, parser):
# Positional arguments
        parser.add_argument('mode', type=int)

    def handle(self, *args, **options):

        global test, deltaDays, trades, mode, compareDeltaRate, debugText
        DBInit = False
        debugText = dateformat.format(datetime.now(), 'Y-m-d H:m:s,')

        if(options['mode'] == 1):
            test = False
            deltaDays = 1
            trades = Trade_BTC_small.objects.order_by('time')
            mode = 1
            compareDeltaRate = 100.0
            debugText+='1,'
        elif(options['mode'] == 2):
            test = False
            deltaDays = 7
            trades = Trade_BTC_medium.objects.order_by('time')
            mode = 2
            compareDeltaRate = 500.0
            debugText+='2,'
        elif(options['mode'] == 3):
            test = False
            deltaDays = 14
            trades = Trade_BTC_large.objects.order_by('time')
            mode = 3
            compareDeltaRate = 1000.0
            debugText+='3,'
        elif(options['mode'] == 0):
            test = True
            deltaDays = 1
            trades = Trade_BTC_test.objects.order_by('time')
            mode = 0
            compareDeltaRate = 100.0
            debugText+='0,'
        if(StopTrade.objects.order_by('time').last().stop == False or mode == 0):

            jsonValue = request_basic(self)
            #jsonValue = request_random(self)

            if('status_code' not in jsonValue):
                lastTrade = trades.last()
#check if init of the db is nessecesary
                #print('check last entry in database')
                if(lastTrade is None):
                    reset_trade(self, 'nothing in DB', jsonValue)
                #elif(lastTrade.time <= (timezone.now()- timedelta(days=deltaDays))):
                #    compareRate = reset_trade(self, 'too old', jasonValue)
                else:
# define the direction of the trade
                    if(lastTrade.eur_to_btc is None):
                        print('set eur_to_btc')
                        set_eur_to_btc(self,lastTrade)
                    #else:
                        #print('eur_to_btc: ' + str(lastTrade.eur_to_btc))

# check if trade should be initiated
                    if(TradeEurBtcTest(self, lastTrade, jsonValue['rate'], compareDeltaRate, mode)):
                        pass
            else:
                print('status_code ' + jsonValue['status_code'])
        else:
            print('Trade stopped')

        if(debug):
            print(debugText)

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

def request_random(self,):
    r = {}
    #r['time'] = dateformat.format(timezone.now(), 'Y-m-d H:m:s')
    r['time'] = dateformat.format(datetime.now(), 'Y-m-d H:m:s')
    r['rate'] = '%.3f' % random.uniform(7500.5, 9000.5)
    #print(str(r['time']) + ' ' + str(r['rate']))
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


################################################################################

def set_eur_to_btc(self, lastTrade):
    lastValue = Total_Value_Test.objects.order_by('time').last()
    if(lastValue is not None):
        if(lastValue.btc is not None and lastValue.eur is not None):
            if(lastValue.btc * lastTrade.rate < lastValue.eur):
                lastTrade.eur_to_btc = False
            elif(lastValue.btc * lastTrade.rate > lastValue.eur):
                lastTrade.eur_to_btc = True
            lastTrade.save()
    else:
        print('No last Value in DB')

def TradeEurBtcTest(self, lastTrade, rate, compareDeltaRate, mode):
    global debugText
    r = False
    deltaRate = lastTrade.rate - float(rate)
    lastValue = Total_Value_Test.objects.order_by('time').last()
    debugText += str(lastTrade.rate) + ',' + str(rate) + ','
    #print('lastTradeRate ' + str(lastTrade.rate) + ' rate ' + str(rate) + ' deltaRate ' + str(deltaRate))
#eur_to_btc from lastTrade, do the other thing
    if(lastValue is not None):
        if(lastTrade.eur_to_btc):
            if(deltaRate < 0 and abs(deltaRate) > compareDeltaRate):
                if(mode == 0):
                    #print('TRADE btc into eur')

                    sellBtc = lastValue.btc
                    buyEur = sellBtc * float(rate)

                    #print('sellBtc ' + str(sellBtc) + ' buyEur ' + str(buyEur))
                    debugText += str(sellBtc) + 'btc,' + str(buyEur) + 'eur,'

                    newValue = Total_Value_Test(eur=buyEur, btc=0)
                    newValue.save()
                    newTrade = Trade_BTC_test(rate=rate,eur=buyEur,btc=sellBtc*-1, eur_to_btc=False)
                    newTrade.save()
                    r = True
                else:
                    pass
            else:
                #print('btc to eur was not traded')
        else:
            if(deltaRate > 0 and abs(deltaRate) > compareDeltaRate):
                if(mode == 0):
                    #print('TRADE eur into btc')

                    sellEur = lastValue.eur
                    buyBtc = sellEur / float(rate)

                    #print(str(sellEur) + ' ' + str(buyBtc))
                    debugText += str(sellEur) + 'eur,' + str(buyBtc) + 'btc,'

                    newValue = Total_Value_Test(eur=0, btc=buyBtc)
                    newValue.save()
                    newTrade = Trade_BTC_test(rate=rate,eur=sellEur*-1,btc=buyBtc, eur_to_btc=True)
                    newTrade.save()
                    r = True
                else:
                    pass
            else:
                #print('eur to btc was not traded')
    else:
        print('No last Value in DB')
    return(r)
