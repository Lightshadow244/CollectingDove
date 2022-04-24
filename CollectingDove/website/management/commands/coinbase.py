from website.classes.CoinbaseTrade import CoinbaseTrade
from website.classes.TradeInfo import TradeInfo
from django.core.management.base import BaseCommand, CommandError
from django.core import serializers

class Command(BaseCommand):
    def handle(self, *args, **options):
        trade = CoinbaseTrade()
        
        

        if(trade.isProfitable()):
            trade.doTrade()
            
        trade.printAndSave()
        #    if(tradeInfo.actualTradeInfo.shouldTrade == False):
        #        tradeInfo.activateShouldTrade()
        #        tradeInfo.inform()
                
        #else:
        #    if(tradeInfo.actualTradeInfo.shouldTrade == True):
        #        tradeInfo.deactivateShouldTradeActivateLastTrade()
        #        tradeInfo.inform()

        #tradeInfo.printAndSaveStatus()
        arr = [trade.actualTrade]
        print(serializers.serialize("json", arr))