from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, timedelta
from django.utils import timezone, dateformat
import requests, random, json, time, hashlib, hmac, time, collections
from website.models import Trade_BTC_small, Trade_BTC_test, Total_Value, Total_Value_Test, StopTrade, Counter
from os import path
from CollectingDove.settings import BASE_DIR

################################################################################

# default settings
deltaDays = 7
compareDeltaRate = 0
trades = {}
mode = 0
debug = 1
debugText = ''
#compareRate = None
header = {}


################################################################################

class Command(BaseCommand):
    def add_arguments(self, parser):
# Positional arguments
        parser.add_argument('mode', type=int)

    def handle(self, *args, **options):

        global deltaDays, trades, rates, mode, compareDeltaRate, debugText
        DBInit = False
        debugText = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")

        ########################################################################
        api = {'key': 'aaa', 'secret': 'aaa'}
        if(path.exists(path.join(BASE_DIR, 'website/apikey.private'),)):
            with open(path.join(BASE_DIR, 'website/apikey.private')) as json_file:
                api = json.load(json_file)
                #api.Key = data['key']
                #api.Secret= data['secret']

        ########################################################################

        if(options['mode'] == 1):
            #deltaDays = 1
            trades = Trade_BTC_small.objects.exclude(btc = None, eur = None).order_by('time')
            rates = Trade_BTC_small.objects.order_by('time')
            mode = 1
            #compareDeltaRate = 100.0
            debugText+='1,'
        elif(options['mode'] == 0):
            #deltaDays = 1
            trades = Trade_BTC_test.objects.exclude(btc = None, eur = None).order_by('time')
            #rates = Trade_BTC_test.objects.exlude(btc => 0, eur => 0).order_by('time')
            rates = Trade_BTC_test.objects.order_by('time')
            mode = 0
            #compareDeltaRate = 100.0
            debugText+='0,'

        #lastValue = Total_Value_Test.objects.order_by('time').last()
        lastValue = getLastFidorReservation(self, api)
        lastTrade = trades.last()
        orders = findOrder(self, lastTrade, api)
        if(StopTrade.objects.order_by('time').last().stop == False or mode == 0):
            if(lastTrade is None):
                reset_trade(self, 'nothing in DB', orders[-1]['price'])
            elif(lastTrade.eur_to_btc is None):
                print('set eur_to_btc')
                set_eur_to_btc(self,lastTrade, lastValue)
            elif(lastValue is None):
                debugText += 'noValue'
            elif(lastValue.eur == -1 and lastTrade.eur_to_btc == False):
                debugText += 'noFidorReservation,'
            else:
                #print(lastTrade.eur_to_btc)
                #print(orders[0])
                #print(orders[-1])

                if(isTradeProfitable(self, lastTrade, orders, rates)):
                    tradeList = initTrade(self, lastTrade, lastValue, orders, api)
                    #if(StopTrade.objects.order_by('time').last().stop == True and mode != 0):
                    finishedTrades = doTrade(self, tradeList, lastTrade.eur_to_btc, api)

                    for trade in finishedTrades:
                        debugText += str(trade['status_code']) + ','
                        debugText += str(trade['order_id']) + ','
                        debugText += str(trade['btc']) + ','
                        debugText += str(trade['price']) + ','
                else:
                    debugText += 'tradeNotProfitable'
        else:
            print('Trade stopped')

        if(debug == 1):
            print(debugText)
        elif(debug == 0):
            if(debugText.count(',') == 6):
                print(debugText)

################################################################################

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

################################################################################

def request_basic(self,):
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
    r['rate'] = '%.3f' % random.uniform(7500.5, 8500.5)
    #print(str(r['time']) + ' ' + str(r['rate']))
    return(r)

################################################################################
def request_curve(self,):
    r = {}
    curve=[8000,7900,7800,7900,7800,7700,7700,7800,7900,7800,7900,8000,8000]
    counter = Counter.objects.get(id=1)

    r['time'] = dateformat.format(datetime.now(), 'Y-m-d H:m:s')
    r['rate'] = curve[counter.counter]
    if(counter.counter == len(curve) - 1):
        counter.counter = 0
    else:
        counter.counter += 1
    counter.save()
    return(r)

################################################################################

def request_rate(self, apiKey, apiSecret):
    r = {'status_code': '1'}
    getParameterJson = {'trading_pair' : 'btceur'}
    getParameter = ''
    postParameter = ''
    nonce = str(int(time.time()))
    http_method = 'GET'
    uri = 'https://api.bitcoin.de/v4/btceur/rates'

    for key in getParameterJson:
        getParameter = getParameter + key + '=' + getParameterJson[key]

    uri = uri + '?' + getParameter
    md5Post = str(hashlib.md5(postParameter.encode()).hexdigest())

    signatur = http_method + '#' + uri + '#' + apiKey + '#' + nonce + '#' + md5Post
    hashedSignatur = hmac.new(apiSecret.encode(), signatur.encode(), hashlib.sha256)

    header = {
    'X-API-KEY':apiKey,
    'X-API-NONCE':nonce,
    'X-API-SIGNATURE':hashedSignatur.hexdigest()
    }
    #print(uri)
    #print(header)

    response = requests.get(uri, headers=header)
    #print(response.json()['credits'])
    if(response.status_code == 200):
        r.clear()
        r['rate'] = response.json()['rates']['rate_weighted']
        r['time'] = dateformat.format(datetime.now(), 'Y-m-d H:m:s')
    return(r)

################################################################################

def reset_trade(self, reason, rate):
    print('reset, ' + reason)
    if(mode == 0):
        t = Trade_BTC_test(rate=rate,eur=0,btc=0)
    elif(mode == 1):
        t = Trade_BTC_small(rate=rate,eur=0,btc=0)
    t.save()


################################################################################

def set_eur_to_btc(self, lastTrade, lastValue):
    #lastValue = Total_Value_Test.objects.order_by('time').last()
    if(lastValue is not None):
        if(lastValue.btc is not None and lastValue.eur is not None):
            if(lastValue.btc * lastTrade.rate < lastValue.eur):
                lastTrade.eur_to_btc = False
            elif(lastValue.btc * lastTrade.rate > lastValue.eur):
                lastTrade.eur_to_btc = True
            lastTrade.save()
    else:
        print('No last Value in DB')

################################################################################

def isTradeProfitable(self, lastTrade, orders, rates):
    global debugText
    r = False
#eur_to_btc from lastTrade, do the other thing
    if(lastTrade.eur_to_btc):
        debugText += 'btcToEur,'
        rate = orders[-1]['price']
        deltaTradeRate = lastTrade.rate - float(rate)
        deltaRate = rates.last().rate - float(rate)
        debugText += str(lastTrade.rate) + ',' + str(rate) + ','

        if(deltaTradeRate < -100 and rates.last().delayTrade == 1 and deltaRate >= 0):
        #if(True):
            debugText += '1,'
            r = True
        elif(deltaTradeRate < 0 and rates.last().delayTrade == 0 and deltaRate < 0):
            debugText += '2,'
            Trade_BTC_test(rate=rate).save()
        elif(deltaTradeRate < 0 and rates.last().delayTrade == 0 and deltaRate >= 0):
            debugText += '3,'
            Trade_BTC_test(rate=rate, delayTrade=1).save()
        elif(deltaTradeRate < 0 and rates.last().delayTrade == 1 and deltaRate < 0):
            debugText += '4,'
            Trade_BTC_test(rate=rate).save()
        else:
            debugText += '5,'
            Trade_BTC_test(rate=rate).save()
            #print('btc to eur was not traded')
    else:
        debugText += 'EurToBtc,'
        rate = orders[0]['price']
        deltaTradeRate = lastTrade.rate - float(rate)
        deltaRate = rates.last().rate - float(rate)
        debugText += str(lastTrade.rate) + ',' + str(rate) + ','

        if(deltaTradeRate > 100 and rates.last().delayTrade == 1 and deltaRate <= 0 ):
        #if(True):
            debugText += '1,'
            r = True
        elif(deltaTradeRate > 0 and rates.last().delayTrade == 0 and deltaRate > 0):
            debugText += '2,'
            Trade_BTC_test(rate=rate).save()
        elif(deltaTradeRate > 0 and rates.last().delayTrade == 0 and deltaRate <= 0):
            debugText += '3,'
            Trade_BTC_test(rate=rate, delayTrade=1).save()
        elif(deltaTradeRate > 0 and rates.last().delayTrade == 1 and deltaRate > 0):
            debugText += '4,'
            Trade_BTC_test(rate=rate).save()
        else:
            debugText += '5,'
            Trade_BTC_test(rate=rate).save()
            #print('eur to btc was not traded')
    return(r)

################################################################################

def findOrder(self, lastTrade, api):

    global debugText
    r = []
    counter = 0
    getParameterJson = {'order_requirements_fullfilled': str(1)}
    #print(lastTrade.eur_to_btc)
    if(lastTrade is None):
        getParameterJson['type'] = 'sell'
    elif(lastTrade.eur_to_btc):
        getParameterJson['type'] = 'sell'
    else:
        getParameterJson['type'] = 'buy'
    getParameter = ''
    postParameter = ''
    nonce = str(int(time.time()))
    http_method = 'GET'
    uri = 'https://api.bitcoin.de/v4/btceur/orderbook'

    #for key in getParameterJson:
    #    getParameter = getParameter + key + '=' + getParameterJson[key] + '&'

    for i, (k,v) in enumerate(getParameterJson.items()):
        if(i == 0):
            getParameter = k + '=' + v
        else:
            getParameter = getParameter + '&' + k + '=' + v

    uri = uri + '?' + getParameter
    #print(uri)
    md5Post = str(hashlib.md5(postParameter.encode()).hexdigest())

    signatur = http_method + '#' + uri + '#' + api['key'] + '#' + nonce + '#' + md5Post
    hashedSignatur = hmac.new(api['secret'].encode(), signatur.encode(), hashlib.sha256)

    header = {
    'X-API-KEY':api['key'],
    'X-API-NONCE':nonce,
    'X-API-SIGNATURE':hashedSignatur.hexdigest()
    }

    response = requests.get(uri, headers=header)

    #data = [
    #{"type":"sell","order_id":"TBQTBM1","price":9400,"max_amount_currency_to_trade":"0.85000000","max_volume_currency_to_pay":7990,"id":0},
    #{"type":"sell","order_id":"TBQTBM2","price":2400,"max_amount_currency_to_trade":"2.85000000","max_volume_currency_to_pay":6840,"id":1},
    #{"type":"sell","order_id":"TBQTBM3","price":9400,"max_amount_currency_to_trade":"1.85000000","max_volume_currency_to_pay":17390,"id":2},
    #{"type":"sell","order_id":"TBQTBM4","price":8400,"max_amount_currency_to_trade":"1.95000000","max_volume_currency_to_pay":16380,"id":3},
    #{"type":"sell","order_id":"TBQTBM5","price":8900,"max_amount_currency_to_trade":"1.05000000","max_volume_currency_to_pay":9345,"id":4}
    #]

    #data = [
    #{"type":"sell","order_id":"TBQTBM1","price":str(request_curve(self,)['rate']),"max_amount_currency_to_trade":"0.85000000",
    #"max_volume_currency_to_pay":'7990',"id":'0','min_volume_currency_to_pay':'1000','min_amount_currency_to_trade':'0.1'},
    #]


    if(response.status_code == 200):
        data = response.json()['orders']

    #print(data)
    r = sorted(data, key = lambda i: i['price'])

    return(r)
################################################################################
def initTrade(self, lastTrade, lastValue, orders, api):
    #print('initiate trade')
    #print('lastValue btc ' + str(lastValue.btc))
    #print('lastValue eur ' + str(lastValue.eur))
    tradeList = []
    if(lastTrade.eur_to_btc):
        counter = -1
        while(float(lastValue.btc) > 0.05 and abs(counter) <= len(orders)):
            trade = {}
            order = orders[counter]
            if(float(order['min_amount_currency_to_trade']) <= lastValue.btc):
                if(float(order['max_amount_currency_to_trade']) > lastValue.btc):
                    sellBtc = lastValue.btc
                    buyEur = sellBtc * float(order['price'])
                else:
                    buyEur = float(order['max_volume_currency_to_pay'])
                    sellBtc = buyEur / float(order['price'])

                lastValue.btc = lastValue.btc - sellBtc

                trade['price'] = order['price']
                trade['order_id'] = order['order_id']
                trade['btc'] = sellBtc
                trade['eur'] = buyEur
                tradeList.append(trade)

            counter = counter - 1

            #print(lastValue.btc)
    else:
        counter = 0
        while(float(lastValue.eur) > 0.1 * float(orders[0]['price']) and counter < len(orders)):
            trade = {}
            order = orders[counter]
            if(float(order['min_volume_currency_to_pay']) <= lastValue.eur):
                if(float(order['max_volume_currency_to_pay']) > lastValue.eur):
                    sellEur = lastValue.eur
                    buyBtc = sellEur / float(order['price'])
                else:
                    buyBtc = float(order['max_amount_currency_to_trade'])
                    sellEur = buyBtc * float(order['price'])

                lastValue.eur = lastValue.eur - sellEur

                trade['price'] = order['price']
                trade['order_id'] = order['order_id']
                trade['btc'] = buyBtc
                trade['eur'] = sellEur
                tradeList.append(trade)
            else:
                print('zu wenig geld')

            counter = counter + 1
    return(tradeList)

###############################################################################

def doTrade(self, tradeList, eur_to_btc, api):
    print(tradeList)
    r = []
    postParameterJson = {}
    postParameter = ''
    nonce = str(int(time.time()))
    http_method = 'POST'


    if(eur_to_btc):
        for trade in tradeList:
            returnTradeInfo = {}
            uri = 'https://api.bitcoin.de/v4/btceur/trades/'
            postParameterJson['amount_currency_to_trade'] = trade['btc']
            postParameterJson['type'] = 'sell'
            postParameterJson = collections.OrderedDict(sorted(postParameterJson.items()))
            #print(postParameterJson)

            for i, (k,v) in enumerate(postParameterJson.items()):
                if(i == 0):
                    postParameter = k + '=' + str(v)
                else:
                    postParameter = postParameter + '&' + k + '=' + str(v)
            #print(postParameter)

            uri = uri + trade['order_id']


            md5Post = str(hashlib.md5(postParameter.encode()).hexdigest())

            signatur = http_method + '#' + uri + '#' + api['key'] + '#' + nonce + '#' + md5Post
            #print(signatur)
            hashedSignatur = hmac.new(api['secret'].encode(), signatur.encode(), hashlib.sha256)

            header = {
            'X-API-KEY':api['key'],
            'X-API-NONCE':nonce,
            'X-API-SIGNATURE':hashedSignatur.hexdigest()
            }

            #print(header)

            if(mode == 1):
                #print('dotrade')
                response = requests.post(uri, headers=header, data=postParameterJson)
                print()
            else:
                response = requests.models.Response()
                response.status_code = 400

            if(response is not None):
                returnTradeInfo['status_code'] = response.status_code
                returnTradeInfo['order_id']  = trade['order_id']
                returnTradeInfo['type']  = postParameterJson['type']
                returnTradeInfo['btc'] =    trade['btc']
                returnTradeInfo['price'] = trade['price']
                r.append(returnTradeInfo)
                if(response.status_code == 201):
                    newTrade = Trade_BTC_small(rate=trade['price'],eur=trade['eur'],btc=trade['btc']  * -1, eur_to_btc=False)
                    newTrade.save()
                elif(mode == 0):
                    newTrade = Trade_BTC_test(rate=trade['price'],eur=trade['eur'],btc=trade['btc']  * -1, eur_to_btc=False)
                    newTrade.save()
                    newValue = Total_Value_Test(eur=Total_Value_Test.objects.order_by('time').last().eur + trade['eur'],btc=Total_Value_Test.objects.order_by('time').last().btc - trade['btc'])
                    #print(newValue.btc)
                    newValue.save()
                elif(response.status_code != 201):
                    print(response.json())
    else:
        for trade in tradeList:
            returnTradeInfo = {}
            uri = 'https://api.bitcoin.de/v4/btceur/trades/'
            postParameterJson['amount_currency_to_trade'] = trade['btc']
            postParameterJson['type'] = 'buy'
            postParameterJson = collections.OrderedDict(sorted(postParameterJson.items()))



            for i, (k,v) in enumerate(postParameterJson.items()):
                if(i == 0):
                    postParameter = k + '=' + str(v)
                else:
                    postParameter = postParameter + '&' + k + '=' + str(v)

            uri = uri + str(trade['order_id'])

            md5Post = str(hashlib.md5(postParameter.encode()).hexdigest())

            signatur = http_method + '#' + uri + '#' + api['key'] + '#' + nonce + '#' + md5Post
            hashedSignatur = hmac.new(api['secret'].encode(), signatur.encode(), hashlib.sha256)

            header = {
            'X-API-KEY':api['key'],
            'X-API-NONCE':nonce,
            'X-API-SIGNATURE':hashedSignatur.hexdigest()
            }

            if(mode == 1):
                response = requests.post(uri, headers=header, data=postParameterJson)
            else:
                response = requests.models.Response()
                response.status_code = 400

            if(response is not None):
                returnTradeInfo['status_code'] = response.status_code
                returnTradeInfo['order_id']  = trade['order_id']
                returnTradeInfo['type']  = postParameterJson['type']
                returnTradeInfo['btc'] =    trade['btc']
                returnTradeInfo['price'] = trade['price']
                r.append(returnTradeInfo)
                if(response.status_code == 201):
                    newTrade = Trade_BTC_small(rate=trade['price'],eur=trade['eur'] * -1,btc=trade['btc'], eur_to_btc=True)
                    newTrade.save()
                elif(mode == 0):
                    newTrade = Trade_BTC_test(rate=trade['price'],eur=trade['eur']  * -1,btc=trade['btc'], eur_to_btc=True)
                    newTrade.save()
                    newValue = Total_Value_Test(eur=Total_Value_Test.objects.order_by('time').last().eur - trade['eur'],btc=Total_Value_Test.objects.order_by('time').last().btc + trade['btc'])
                    #print(newValue.eur)
                    newValue.save()
                elif(resonse.status_code != 201):
                    print(response.json())
    #print(r)
    return(r)

def getLastFidorReservation(self, api):
    r = Total_Value_Test(0,0)
    getParameterJson = {}
    getParameter = ''
    postParameter = ''
    nonce = str(int(time.time()))
    http_method = 'GET'
    uri = 'https://api.bitcoin.de/v4/account'

    md5Post = str(hashlib.md5(postParameter.encode()).hexdigest())

    signatur = http_method + '#' + uri + '#' + api['key'] + '#' + nonce + '#' + md5Post
    hashedSignatur = hmac.new(api['secret'].encode(), signatur.encode(), hashlib.sha256)

    header = {
    'X-API-KEY':api['key'],
    'X-API-NONCE':nonce,
    'X-API-SIGNATURE':hashedSignatur.hexdigest()
    }

    response = requests.get(uri, headers=header)

    if(response.status_code == 200):
        data = response.json()['data']
        if('fidor_reservation' in data):
            #print(response.json()['data'])
            r.eur = float(data['fidor_reservation']['available_amount'])
        else:
            r.eur = -1
        r.btc = float(data['balances']['btc']['available_amount'])

        if(mode == 0):
            r.eur = Total_Value_Test.objects.order_by('time').last().eur
            r.btc = Total_Value_Test.objects.order_by('time').last().btc

    else:
        #r['status_code'] = response.status_code
        print(response.status_code)
    return(r)
