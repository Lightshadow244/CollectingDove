from django.core.management.base import BaseCommand, CommandError
from os import path
from CollectingDove.settings import BASE_DIR
from website.models import Trade_BTC_small, Trade_BTC_test, Total_Value, Total_Value_Test, StopTrade, Counter
import requests, random, json, time, hashlib, hmac, time, collections
from datetime import datetime, timedelta
from django.utils import timezone, dateformat

debugText = ''
mode = 0

class Command(BaseCommand):
    def add_arguments(self, parser):
# Positional arguments
        parser.add_argument('mode', type=int)

    def handle(self, *args, **options):
        #print("test")

        global debugText, mode

        ########################################################################
        api = {'key': 'aaa', 'secret': 'aaa'}
        if(path.exists(path.join(BASE_DIR, 'website/apikey.private'),)):
            with open(path.join(BASE_DIR, 'website/apikey.private')) as json_file:
                api = json.load(json_file)
        ########################################################################

        trades = Trade_BTC_small.objects.exclude(btc = None, eur = None).order_by('time')
        rates = Trade_BTC_small.objects.order_by('time')
        mode = 1
        debugText+='1,'

        lastTrade = trades.last()
        orders = findOrder(self, lastTrade, api)
        lastValue = getLastFidorReservation(self, api, lastTrade.eur_to_btc)

        if(lastTrade is None):
            debugText += "lastTradeNone,"
        elif(lastTrade.eur_to_btc is None):
            debugText += "eurToBtcNone,"
        else:
            if(lastValue is None):
                debugText += 'noValue'
            elif(lastValue.eur == -1):
                debugText += 'noFidorReservation,'
            else:
                tradeList = initTrade(self, lastTrade, lastValue, orders, api)
                finishedTrades = doTrade(self, tradeList, lastTrade.eur_to_btc, api)

                for trade in finishedTrades:
                    debugText += str(trade['status_code']) + ','
                    debugText += str(trade['order_id']) + ','
                    debugText += str(trade['btc']) + ','
                    debugText += str(trade['price']) + ','
        print(debugText)
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
    if(response is not None):
        if(response.status_code == 200):
            data = response.json()['orders']
    r = sorted(data, key = lambda i: i['price'])
    return(r)

################################################################################

def getLastFidorReservation(self, api, eur_to_btc):
    global debugText
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
        elif(eur_to_btc):
            r.eur = 0
        else:
            r.eur = -1
        r.btc = float(data['balances']['btc']['available_amount'])
    else:
            debugText += 'Connection to bitcoin failed,'
    return(r)

################################################################################

def initTrade(self, lastTrade, lastValue, orders, api):
    print("inittrade")
    tradeList = []
    print(lastTrade.eur_to_btc)
    print(lastValue.eur)
    if(lastTrade.eur_to_btc):
        counter = -1
        while(abs(counter) <= len(orders)):
            trade = {}
            order = orders[counter]
            if(float(order['min_amount_currency_to_trade']) <= lastValue.btc):
                if(float(order['max_amount_currency_to_trade']) > lastValue.btc):
                    sellBtc = lastValue.btc
                    buyEur = sellBtc * float(order['price'])
                else:
                    buyEur = float(order['max_volume_currency_to_pay'])
                    sellBtc = float(order['max_amount_currency_to_trade'])

                lastValue.btc = lastValue.btc - sellBtc

                trade['price'] = order['price']
                trade['order_id'] = order['order_id']
                trade['btc'] = float(str(sellBtc)[:15])
                trade['eur'] = buyEur
                tradeList.append(trade)

            counter = counter - 1

            #print(lastValue.btc)
    else:
        counter = 0
        while(counter < len(orders)):
            trade = {}
            order = orders[counter]
            if(float(order['min_volume_currency_to_pay']) <= lastValue.eur):
                if(float(order['max_volume_currency_to_pay']) > lastValue.eur):
                    sellEur = lastValue.eur
                    buyBtc = sellEur / float(order['price'])
                else:
                    buyBtc = float(order['max_amount_currency_to_trade'])
                    sellEur = float(order['max_volume_currency_to_pay'])

                lastValue.eur = lastValue.eur - sellEur

                trade['price'] = order['price']
                trade['order_id'] = order['order_id']
                trade['btc'] = float(str(buyBtc)[:15])
                trade['eur'] = sellEur
                tradeList.append(trade)
            #else:
            #    print('zu wenig geld')

            counter = counter + 1
    return(tradeList)

def doTrade(self, tradeList, eur_to_btc, api):
    #print(tradeList)
    r = []
    postParameterJson = {}
    postParameter = ''
    http_method = 'POST'


    if(eur_to_btc):
        for trade in tradeList:
            nonce = str(int(time.time()))
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

#traderesponse
            #response = requests.post(uri, headers=header, data=postParameterJson)
            response = requests.models.Response()

            if(response is not None):
                returnTradeInfo['status_code'] = response.status_code
                returnTradeInfo['order_id']  = trade['order_id']
                returnTradeInfo['type']  = postParameterJson['type']
                returnTradeInfo['btc'] =    trade['btc']
                returnTradeInfo['price'] = trade['price']
                r.append(returnTradeInfo)
                if(response.status_code == 201 and mode == 1):
                    newTrade = Trade_BTC_small(rate=trade['price'],eur=trade['eur'],btc=trade['btc']  * -1, eur_to_btc=False)
                    newTrade.save()
                    newValue = Total_Value(eur=Total_Value.objects.order_by('time').last().eur + trade['eur'],btc=Total_Value.objects.order_by('time').last().btc - trade['btc'])
                    newValue.save()
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
            nonce = str(int(time.time()))
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

#traderesponse
            #response = requests.post(uri, headers=header, data=postParameterJson)
            response = requests.models.Response()

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
                    newValue = Total_Value(eur=Total_Value.objects.order_by('time').last().eur - trade['eur'],btc=Total_Value.objects.order_by('time').last().btc + trade['btc'])
                    newValue.save()
                elif(mode == 0):
                    newTrade = Trade_BTC_test(rate=trade['price'],eur=trade['eur']  * -1,btc=trade['btc'], eur_to_btc=True)
                    newTrade.save()
                    newValue = Total_Value_Test(eur=Total_Value_Test.objects.order_by('time').last().eur - trade['eur'],btc=Total_Value_Test.objects.order_by('time').last().btc + trade['btc'])
                    #print(newValue.eur)
                    newValue.save()
                elif(response.status_code != 201):
                    print(response.json())
    #print(r)
    return(r)
