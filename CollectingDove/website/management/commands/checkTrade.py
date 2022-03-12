from website.classes.TradeInfo import TradeInfo
from django.core.management.base import BaseCommand, CommandError
from website.models import StopTrade

class Command(BaseCommand):
    def handle(self, *args, **options):
        tradeInfo = TradeInfo()

        # check btc status on bitcoin.de
        # if buyBtc = true und btc > btc letzter stand dann change buybtc to False
        if(tradeInfo.lastTrade.shouldTrade):
            tradeInfo.validateBtcStatus()

        if(tradeInfo.isTradeProfitable()):
            if(tradeInfo.lastTrade.shouldTrade == False):
                tradeInfo.activateShouldTrade()
                tradeInfo.inform()
        else:
            if(tradeInfo.lastTrade.shouldTrade == True):
                tradeInfo.deactivateShouldTrade()
                tradeInfo.inform()




        #if(True):
            #if(trade.eurToBtc == False):
            #    trade.reserveValue()
            #    trade.orders = trade.getOrders()
            #trade.getTradeOrders()
            #trade.executeTrade()



        #print(trade.status)