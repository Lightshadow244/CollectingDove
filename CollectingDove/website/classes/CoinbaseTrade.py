from logging import exception
from website.models import CoinbaseTradeModel
from website.classes.CoinbaseAPI import CoinbaseAPI
import json
from django.core import serializers

class CoinbaseTrade:
    def __init__(self):
        self.logLevel = 1
        
        self.api = CoinbaseAPI()
        
        self.lastRate = CoinbaseTradeModel.objects.order_by('time').last()
        if self.lastRate is None:
            raise Exception("No trade in db")

        self.lastTrade = CoinbaseTradeModel.objects.exclude(isTrade = False).order_by('time').last()
        if self.lastTrade is None:
            raise Exception("No lastTrade in db")

        self.actualTrade = CoinbaseTradeModel(
            buyBtc      = self.lastRate.buyBtc,
            isTrade     = False
        )    

        if self.lastRate.isTrade:
            self.actualTrade.buyBtc = not self.actualTrade.buyBtc

        self.setEurAndBtc()
        self.getCoinbaseRate()

    def setEurAndBtc(self):
        for a in self.api.accounts:
            if a["name"] == "Euro Wallet":
                self.actualTrade.eur = float(a["balance"]["amount"])
            elif a["name"] == "BTC Wallet":
                self.actualTrade.btc = float(a["balance"]["amount"])

    def getCoinbaseRate(self):
        cbRate = self.api.getPrice(self.actualTrade.buyBtc)
        self.actualTrade.rate = float(cbRate['amount'])

    def isProfitable(self):
        r = False

        rate = self.actualTrade.rate
        deltaTradeRate = self.lastTrade.rate - float(rate)

        if(self.actualTrade.buyBtc == False):

            self.log('lastTradeRate,' + str(self.lastTrade.rate) + ' rate,' + str(rate))
            
            profitValue = self.lastTrade.rate * 0.04
            #debugText += 'dtr: ' + str(deltaTradeRate) + ', dr: ' + str(deltaRate) + ','

            #newRate = Trade_BTC(rate=rate)

            if(deltaTradeRate < profitValue * -1 and deltaTradeRate > self.lastRate.peakRate * 0.85):
                self.actualTrade.status = "1"
                r = True
            elif(deltaTradeRate < self.lastRate.peakRate):
                self.actualTrade.status = "2"
                self.actualTrade.peakRate = deltaTradeRate
            else:
                self.actualTrade.status = "3"
        else:
            
            self.log('lastTradeRate,' + str(self.lastTrade.rate) + ' rate,' + str(rate))

            profitValue = self.lastTrade.rate * 0.04

            if(deltaTradeRate > profitValue and deltaTradeRate < self.lastRate.peakRate * 0.85):
                self.actualTrade.status = "1"
                r = True
            elif(deltaTradeRate > self.lastRate.peakRate):
                self.actualTrade.status = "2"
                self.actualTrade.peakRate = deltaTradeRate
            else:
                self.actualTrade.status = "3"
        
        self.log('profitValue=' + str(profitValue))
        self.log('peak=' + str(self.lastRate.peakRate))
        self.log('peak*0.85=' + str(self.lastRate.peakRate * 0.85))
        self.log('delta=' + str(deltaTradeRate))

        return(r)
        #return(True)
        
    def doTrade(self):
        if self.actualTrade.buyBtc:
            self.api.postBuy(self.actualTrade.eur)
        else:
            self.api.postSell(self.actualTrade.btc)

    def printAndSave(self):
        self.actualTrade.save()
        arr = {self.actualTrade}
        print(serializers.serialize("json", arr))

    def logJson(self, j):
        if self.logLevel == 1:
            print(json.dumps(j, indent=2, sort_keys=True))
    
    def logObject(self, o):
        if self.logLevel == 1:
            arr = [o]
            print(serializers.serialize("json", arr))

    def log(self, s):
        if self.logLevel == 1:
            print(s)
