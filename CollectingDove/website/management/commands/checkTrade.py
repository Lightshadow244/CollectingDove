from website.classes.TradeInfo import TradeInfo
from django.core.management.base import BaseCommand, CommandError
from website.models import StopTrade

class Command(BaseCommand):
    def handle(self, *args, **options):
        tradeInfo = TradeInfo()

        if(tradeInfo.isTradeProfitable()):
            if(tradeInfo.actualTradeInfo.shouldTrade == False):
                tradeInfo.activateShouldTrade()
                tradeInfo.inform()
                
        else:
            if(tradeInfo.actualTradeInfo.shouldTrade == True):
                tradeInfo.deactivateShouldTradeActivateLastTrade()
                tradeInfo.inform()

        tradeInfo.printAndSaveStatus()




        #if(True):
            #if(trade.eurToBtc == False):
            #    trade.reserveValue()
            #    trade.orders = trade.getOrders()
            #trade.getTradeOrders()
            #trade.executeTrade()



        #print(trade.status)