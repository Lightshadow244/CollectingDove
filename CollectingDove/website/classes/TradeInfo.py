from website.models import TradeInfoModel
import hashlib, requests, hmac, time

class TradeInfo:
    def __init__(self):
        self.logLevel = 1
        self.log("test")

        self.lastTrade = TradeInfoModel.objects.order_by('time').last()
        if self.lastTrade is None:
             raise Exception("")

    def getOrders(self):
        self.log("getOrders")
        getParameterJson = {'order_requirements_fullfilled': str(1)}
        if(self.lastTrade is None):
            getParameterJson['type'] = 'sell'
        elif(self.lastTrade.buyBtc):
            getParameterJson['type'] = 'buy'
        else:
            getParameterJson['type'] = 'sell'
        
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

        self.log(uri)

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

    def log(self, s):
        if(self.logLevel == 1):
            print(s)