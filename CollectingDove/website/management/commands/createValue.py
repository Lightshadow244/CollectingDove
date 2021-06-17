from django.core.management.base import BaseCommand, CommandError
from website.models import Total_Value

class Command(BaseCommand):
    def handle(self, *args, **options):
        #eur = 10000.0
        #btc = 0.0
        btc = 0
        eur = 5000
        Total_Value(eur=eur,btc=btc).save()
        print('created value eur= ' + str(eur) + ' btc= ' + str(btc))
