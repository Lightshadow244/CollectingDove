from django.core.management.base import BaseCommand, CommandError
from website.models import Total_Value
import random, time
from django.utils import timezone
from website.classes.CoinbaseAPI import CoinbaseAPI

class Command(BaseCommand):
    def handle(self, *args, **options):
        api = CoinbaseAPI()
        #api.postBuy(50.0)

        for a in api.accounts:
            if a["name"] == "BTC Wallet":
                btc = float(a["balance"]["amount"])

        api.postSell(float(btc))

        

        

