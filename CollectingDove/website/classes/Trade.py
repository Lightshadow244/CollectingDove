from os import path
from CollectingDove.settings import BASE_DIR
from website.models import Trade_BTC_small, Total_Value, StopTrade, Counter
from datetime import datetime, timedelta
from django.utils import timezone
import requests, random, json, time, hashlib, hmac, time, collections

class Trade:
    def __init__(self):
        
        self.status = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S") + ','

        self.api = {}
        if(path.exists(path.join(BASE_DIR, 'website/apikey.private'),)):
            with open(path.join(BASE_DIR, 'website/apikey.private')) as json_file:
                self.api = json.load(json_file)

        self.pastTrades = Trade_BTC_small.objects.exclude(btc = None, eur = None).order_by('time')
        self.rates = Trade_BTC_small.objects.order_by('time')

        self.lastTrade = self.pastTrades.last()

        self.orders = self.findOrder()

    def findOrder(self):
        getParameterJson = {'order_requirements_fullfilled': str(1)}
        if(self.lastTrade is None):
            getParameterJson['type'] = 'sell'
        elif(self.lastTrade.eur_to_btc):
            getParameterJson['type'] = 'sell'
        else:
            getParameterJson['type'] = 'buy'
        
        getParameter = ''
        postParameter = ''
        nonce = str(int(time.time()))
        http_method = 'GET'
        uri = 'https://api.bitcoin.de/v4/btceur/orderbook'

        for i, (k,v) in enumerate(getParameterJson.items()):
            if(i == 0):
                getParameter = k + '=' + v
            else:
                getParameter = getParameter + '&' + k + '=' + v

        uri = uri + '?' + getParameter
        print(uri)
        md5Post = str(hashlib.md5(postParameter.encode()).hexdigest())

        signatur = http_method + '#' + uri + '#' + self.api['key'] + '#' + nonce + '#' + md5Post
        hashedSignatur = hmac.new(self.api['secret'].encode(), signatur.encode(), hashlib.sha256)

        header = {
        'X-API-KEY':self.api['key'],
        'X-API-NONCE':nonce,
        'X-API-SIGNATURE':hashedSignatur.hexdigest()
        }
        response = requests.get(uri, headers=header)
        if(response is not None):
            if(response.status_code == 200):
                data = response.json()['orders']
        r = sorted(data, key = lambda i: i['price'])

        return(r)