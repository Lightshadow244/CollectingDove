from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, timezone, timedelta
from website.models import Trade_BTC, Graph_RatesPerDay
import json

class Command(BaseCommand):
    def handle(self, *args, **options):
        lastDay = datetime.now() - timedelta(days=1)
        #lastDay = datetime(2020,9,13,0,0,0)
        lastDay = lastDay.replace(tzinfo=timezone.utc,hour=0, minute=0, second=0, microsecond=0)

        today = datetime.now()
        #today = datetime.now()- timedelta(days=1)
        today = today.replace(tzinfo=timezone.utc,hour=0, minute=0, second=0, microsecond=0)

        ratesLastDay = Trade_BTC.objects.filter(time__gte=lastDay, time__lte=today).order_by('time')

        sumRate = 0.0

        trades = []
        for rate in ratesLastDay:
            sumRate += rate.rate
            #print(sumRate)

            if(rate.btc is not None and rate.eur is not None):
                trade={}
                trade['time'] = rate.time.strftime("%H:%M")
                trade['rate'] = float('%.2f' % rate.rate)
                trade['eur'] = float('%.2f' % rate.eur)
                trades.append(trade)

        #print(json.dumps(trades))
        sumRate = float('%.2f' % (sumRate/ratesLastDay.count()))
        #print(sumRate)

        ratePerDay = Graph_RatesPerDay(rate=sumRate,time=lastDay,trades=json.dumps(trades))
        ratePerDay.save()
