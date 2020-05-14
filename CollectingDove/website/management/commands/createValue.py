from django.core.management.base import BaseCommand, CommandError
from website.models import Total_Value_Test

class Command(BaseCommand):
    def handle(self, *args, **options):
        eur = 10000.0
        btc = 0.0
        Total_Value_Test(eur=eur,btc=btc).save()
        print('created value eur= ' + str(eur) + ' btc= ' + str(btc))
