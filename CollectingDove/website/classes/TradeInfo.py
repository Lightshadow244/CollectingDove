from website.models import TradeInfoModel
import hashlib, requests, hmac, time

class TradeInfo:
    def __init__(self):
        self.logLevel = 1
        self.log("test")

        self.lastTrade = TradeInfoModel.objects.order_by('time').last()
        if self.lastTrade is None:
             raise Exception("No trade in db")

        self.buyBtc = self.lastTrade.buyBtc
        self.shouldTrade = self.lastTrade.shouldTrade
        

        # check btc status on bitcoin.de
        # if buyBtc = true und btc > btc letzter stand dann change buybtc to False
        if(self.shouldTrade):
            self.validateBtcStatus()
        
        if(self.buyBtc):
            orders = self.getOrders("buy")
            self.rate = orders[-1]['price']
        else:
            orders = self.getOrders("sell")
            self.rate = orders[0]['price']

        self.actualTradeInfo = TradeInfo(rate=self.rate,buyBtc=self.buyBtc, shouldTrade=self.shouldTrade)

    def getOrders(self, type:str):
        self.log("getOrders")
        getParameterJson = {'order_requirements_fullfilled': str(1)}
        if(str != "sell" and str != "buy"):
            raise Exception("failed to get Orders, getOrders not sell or buy")

        getParameterJson['type'] = type

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

    def validateBtcStatus(self):
        currentBtc = self.getCurrentBtc()

        if(self.buyBtc):
            if(currentBtc > self.lastTrade.btc):
                # btc wurde gekauft
                self.buyBtc = False
                self.deactivateShouldTrade()
        else:
            if(currentBtc < self.lastTrade.btc):
                # btc wurde verkauft
                self.buyBtc = True
                self.deactivateShouldTrade()

    def activateShouldTrade(self):
        self.shouldTrade = True

    def deactivateShouldTrade(self):
        self.shouldTrade = False

    def log(self, s):
        if(self.logLevel == 1):
            print(s)