from django.core.management.base import BaseCommand, CommandError
from website.models import Trade_BTC, Total_Value
import requests, json
from os import path
from CollectingDove.settings import BASE_DIR

#python manage.py 5000 0 42000

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('eur', type=float)
        parser.add_argument('btc', type=float)
        parser.add_argument('rate', type=float)

    def handle(self, *args, **options):

        if(path.exists(path.join(BASE_DIR, 'website/apikey_basic.private'),)):
            with open(path.join(BASE_DIR, 'website/apikey_basic.private')) as json_file:
                api = json.load(json_file)
        else:
            raise Exception("no api credentials were given")

        if(options['eur'] > options['btc']):
            eurToBtc = False
        elif(options['eur'] < options['btc']):
            eurToBtc = True

        #https://api.bitcoin.de/v4/:trading_pair/basic/rate.json?apikey=YOUR_API_KEY
        #uri = "https://api.bitcoin.de/v4/btceur/basic/rate.json?apikey=" + api['key']
        #response = requests.get(uri)

        #if(response is not None):
        #    if(response.status_code == 200):
        #        #print(response.json()['rate']['rate_weighted'])
        #        Trade_BTC(eur_to_btc=eurToBtc,rate=response.json()['rate']['rate_weighted'],eur=options['eur'],btc=options['btc']).save()
        #        Total_Value(eur=options['eur'],btc=options['btc']).save()
        #    else:
        #        print(response.json())


        Trade_BTC(eur_to_btc=eurToBtc,rate=options['rate'],eur=options['eur'],btc=options['btc']).save()
        Total_Value(eur=options['eur'],btc=options['btc']).save()

        
        