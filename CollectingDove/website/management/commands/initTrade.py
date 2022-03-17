from django.core.management.base import BaseCommand, CommandError
from website.classes.Trade import Trade
from website.models import TradeInfoModel

class Command(BaseCommand):
    #def add_arguments(self):
# Positional arguments
        #parser.add_argument('eur', type=float)
        #parser.add_argument('rate', type=float)

    def handle(self, *args, **options):
        #Trade_BTC(eur_to_btc=False,rate=options['rate'],eur=options['eur'],btc=0).save()
        #Total_Value(eur=options['eur'],btc=0).save()
        TradeInfoModel(rate=40500.0,buyBtc=True, shouldTrade=False, lastTrade=True).save()

