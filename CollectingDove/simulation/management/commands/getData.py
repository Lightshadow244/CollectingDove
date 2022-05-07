from django.core.management.base import BaseCommand
from django.utils import timezone
from CollectingDove.settings import BASE_DIR

from os import path
import requests, json, time

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class Command(BaseCommand):
    def handle(self, *args, **options):

        if(path.exists(path.join(BASE_DIR, 'simulation/.firebase-api-key.json'),)):
            firebase_cred = credentials.Certificate("simulation/.firebase-api-key.json")
        else:
            raise Exception("no api credentials were given")

        ### get btc rate ###

        url = 'https://api.cryptowat.ch/markets/kraken/btceur/price'
        headers = {}
        response = requests.get(url, headers=headers).json()

        data = {
            "rate": response['result']['price'],
            "timestamp": str(time.mktime(timezone.localtime(timezone.now()).timetuple()))[:-2]
        }

        print(data)

        ### store to firestore ###

        firebase_admin.initialize_app(firebase_cred)

        db = firestore.client()
        doc_ref = db.collection('rates').document(data["timestamp"])

        doc_ref.set({ 
            'rate':data["rate"]
        })

