from website.classes.Trade import Trade
from django.core.management.base import BaseCommand, CommandError
from website.models import StopTrade

class Command(BaseCommand):
    def handle(self, *args, **options):
        trade = Trade()

        if(trade.isTradeProfitable()):
            if(trade.eurToBtc == False):
                trade.reserveValue()
                trade.orders = trade.getOrders()
            trade.getTradeOrders()
            trade.executeTrade()



        print(trade.status)