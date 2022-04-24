from django.core.management.base import BaseCommand
from website.models import TradeInfoModel
from website.models import CoinbaseTradeModel

class Command(BaseCommand):
    #def add_arguments(self):
# Positional arguments
        #parser.add_argument('eur', type=float)
        #parser.add_argument('rate', type=float)

    def handle(self, *args, **options):
        #Trade_BTC(eur_to_btc=False,rate=options['rate'],eur=options['eur'],btc=0).save()
        #Total_Value(eur=options['eur'],btc=0).save()
        #TradeInfoModel(rate=40500.0,buyBtc=False, shouldTrade=False, lastTrade=True).save()
        
        #CoinbaseTradeModel(rate=30000.0,buyBtc=True,isTrade=True,btc=1.0).save()
        lastTrade = CoinbaseTradeModel.objects.exclude(isTrade = False).order_by('time').last()
        print(lastTrade.rate)

