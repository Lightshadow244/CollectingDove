from django.core.management.base import BaseCommand, CommandError
from website.models import Total_Value, Test
import random, time
from django.utils import timezone

class Command(BaseCommand):
    def handle(self, *args, **options):
        #eur = 10000.0
        #btc = 0.0
        #btc = 0
        #eur = 5000
        #Total_Value(eur=eur,btc=btc).save()
        #print('created value eur= ' + str(eur) + ' btc= ' + str(btc))

        v = random.randrange(0, 40000.0)
        y = str(time.mktime(timezone.now().timetuple()))
        y = y[:-2]

        Test(time=y,value=v).save()
        print(v)
        print(y)

        x = Test.objects.all().count()

        print(x)

        

        

