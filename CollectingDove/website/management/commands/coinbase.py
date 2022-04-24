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
       
        arr = [trade.actualTrade]
        print(serializers.serialize("json", arr))