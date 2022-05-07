from django.core.management.base import BaseCommand
import requests, json, time
from django.utils import timezone

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class Command(BaseCommand):
    def handle(self, *args, **options):
        url = 'https://api.cryptowat.ch/markets/kraken/btceur/price'
        headers = {}
        response = requests.get(url, headers=headers).json()

        data = {
            "rate": response['result']['price'],
            "timestamp": str(time.mktime(timezone.localtime(timezone.now()).timetuple()))[:-2]
        }

        print(data)

        cred = credentials.Certificate("../firebase-api-key.json")
        firebase_admin.initialize_app(cred)

        db = firestore.client()
        doc_ref = db.collection('rates').document(data["timestamp"])

        doc_ref.set({ 
            'rate':data["rate"]
        })

