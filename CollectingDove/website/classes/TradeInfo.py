from email.message import EmailMessage
from logging import exception
from website.models import TradeInfoModel
from CollectingDove.settings import BASE_DIR
from os import path
import hashlib, requests, hmac, time, json, smtplib, ssl
from django.core import serializers

class TradeInfo:
    def __init__(self):
        self.logLevel = 0
        
        if(path.exists(path.join(BASE_DIR, 'website/apikey.private'),)):
            with open(path.join(BASE_DIR, 'website/apikey.private')) as json_file:
                self.api = json.load(json_file)
        else:
            raise Exception("no api credentials were given")


        self.lastRateInfo = TradeInfoModel.objects.order_by('time').last()
        if self.lastRateInfo is None:
            raise Exception("No trade in db")
            #self.initTradeInfoInDb()
            #self.lastRateInfo = TradeInfoModel.objects.order_by('time').last()

        self.lastTradeInfo = TradeInfoModel.objects.exclude(lastTrade = False).order_by('time').last()
        if self.lastTradeInfo is None:
            raise Exception("No lastTrade in db")

        self.buyBtc = self.lastRateInfo.buyBtc
        self.shouldTrade = self.lastRateInfo.shouldTrade
        self.btc = self.lastRateInfo.btc
        self.lastTrade = False
        

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

        #self.log("rate: " + str(self.rate))
        #self.log("buyBtc: " + str(self.buyBtc))
        #self.log("shouldTrade: " + str(self.shouldTrade))
        
        self.actualTradeInfo = TradeInfoModel(
            rate            = self.rate,
            buyBtc          = self.buyBtc, 
            shouldTrade     = self.shouldTrade,
            peakRate        = self.lastRateInfo.peakRate,
            btc             = self.btc,
            lastTrade       = self.lastTrade
        )

    def getOrders(self, type:str):
        self.log("getOrders")
        getParameterJson = {'order_requirements_fullfilled': str(1)}
        if(type != "sell" and type != "buy"):
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
        self.log("validate btc status")
        currentBtc = self.getCurrentBtc()

        if(self.buyBtc):
            if(currentBtc > self.btc):
                # btc wurde gekauft
                self.buyBtc = False
                self.deactivateShouldTradeActivateLastTrade()
                self.btc = currentBtc
        else:
            if(currentBtc < self.btc):
                # btc wurde verkauft
                self.buyBtc = True
                self.deactivateShouldTradeActivateLastTrade()
                self.btc = currentBtc

    def getCurrentBtc(self):
        self.log("get current btc")

        postParameter = ''
        nonce = str(int(time.time()))
        http_method = 'GET'
        uri = 'https://api.bitcoin.de/v4/account'

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
                data = response.json()
                r = data['data']["balances"]["btc"]["available_amount"]
            else:
                self.log(response._content)
                raise Exception("Error retrieving data")
        return(float(r))

    def initTradeInfoInDb(self):
        self.log("init tradeInfo in db")
        currentBtc = float(self.getCurrentBtc())

        if currentBtc > 0.001:
            orders = self.getOrders("sell")
            price = orders[0]['price']
            buyBtc = False
        else:
            orders = self.getOrders("buy")
            price = orders[-1]['price']
            buyBtc = True

        TradeInfoModel(rate=price,buyBtc=buyBtc, shouldTrade=False).save()

    def isTradeProfitable(self):
        self.log("isTradeProfitable")
        r = False

        rate = self.rate
        deltaTradeRate = self.lastTradeInfo.rate - float(rate)

        if(self.buyBtc == False):

            self.log('lastTradeRate,' + str(self.lastTradeInfo.rate) + ' rate,' + str(rate))
            
            profitValue = self.lastTradeInfo.rate * 0.01
            #debugText += 'dtr: ' + str(deltaTradeRate) + ', dr: ' + str(deltaRate) + ','

            #newRate = Trade_BTC(rate=rate)

            if(deltaTradeRate < profitValue * -1 and deltaTradeRate > self.lastRateInfo.peakRate * 0.85):
                self.log("1")
                r = True
            elif(deltaTradeRate < self.lastRateInfo.peakRate):
                self.log("2")
                self.actualTradeInfo.peakRate = deltaTradeRate
            else:
                self.log("3")
        else:
            
            self.log('lastTradeRate,' + str(self.lastTradeInfo.rate) + ' rate,' + str(rate))

            profitValue = self.lastTradeInfo.rate * 0.01

            if(deltaTradeRate > profitValue and deltaTradeRate < self.lastRateInfo.peakRate * 0.85):
                self.log("1")
                r = True
            elif(deltaTradeRate > self.lastRateInfo.peakRate):
                self.log("2")
                self.actualTradeInfo.peakRate = deltaTradeRate
            else:
                self.log("3")
                #self.actualTradeInfo.peakRate = self.actualTradeInfo.peakRate
        #if(r == False):
        #    self.status += 'tradeNotProfitable,'

        #self.status += "peak," + str(self.lastTradeRate.highest_peak) + ","
        #self.status += "border," + str(self.lastTradeRate.highest_peak * 0.85) + ","
        #self.status += "delta," + str(deltaTradeRate) + ","
        
        self.log('profitValue=' + str(profitValue))
        self.log('peak=' + str(self.lastRateInfo.peakRate))
        self.log('peak*0.85=' + str(self.lastRateInfo.peakRate * 0.85))
        self.log('delta=' + str(deltaTradeRate))

        return(r)
    
    def inform(self):

        msg = EmailMessage()
        msg["From"] = self.api["gmail_login"]
        msg["To"] = self.api["gmail_receiver"]

        if self.actualTradeInfo.shouldTrade:
            msg["Subject"] = "[collectingDove] o o o"
        else:
            msg["Subject"] = "[collectingDove] x x x"

        if self.actualTradeInfo.buyBtc:
            msg.set_content("rate: {rate} | lastRate: {lastRate} | buy btc".format(rate=self.actualTradeInfo.rate, lastRate=self.lastRateInfo.rate))
        else:
            msg.set_content("rate: {rate} | lastRate: {lastRate}| sell btc".format(rate=self.actualTradeInfo.rate, lastRate=self.lastRateInfo.rate))

        self.sendMail(msg)
       

        

    def printAndSaveStatus(self):

        self.actualTradeInfo.save()

        arr = [self.actualTradeInfo]
        print(serializers.serialize("json", arr))

    def activateShouldTrade(self):
        self.shouldTrade = True

    def deactivateShouldTradeActivateLastTrade(self):
        self.shouldTrade = False
        self.lastTrade = True

    def saveRate(self):
        pass

    def log(self, s):
        if(self.logLevel == 1):
            print(s)

    def sendMail(self, msg):
        port = 465  # For SSL
        login = self.api["gmail_login"]
        password = self.api["gmail_password"]

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(login, password)
            #server.sendmail(login, receiver, body)
            server.send_message(msg)