from django.shortcuts import render
from django.http import HttpResponse
from website.models import Trade_BTC_test, StopTrade, Trade_BTC
from django.template import loader
import csv
from datetime import datetime, timezone, timedelta


def index(request):
    template = loader.get_template('CollectingDove/index.html')

    #letzten zwei Tage 12 DP in einer Stunde * 48 Stunden = 576 Datenpunkte
    last2d = datetime.now() - timedelta(days=2)
    last2d = last2d.replace(tzinfo=timezone.utc)
    rates_2d = Trade_BTC.objects.filter(time__gte=last2d).order_by('time')
    trades_2d = Trade_BTC.objects.filter(time__gte=last2d).exclude(btc = None, eur = None).order_by('time')

    label = []
    t = 0
    for rate in rates_2d:
        if(rate.time.hour > t):
            t = rate.time.hour
            label.append(t)
        else:
            label.append(None)
    print(label)



    context = {
    }
    return HttpResponse(template.render(context, request))

def exportValue(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    writer.writerow(['time', 'rate', 'eur', 'btc'])

    for trade in Trade_BTC_test.objects.order_by('time'):
        writer.writerow([trade.time, trade.rate, trade.eur, trade.btc])

    return response

def stopTrade(request):
    StopTrade(stop=True).save()
    return HttpResponse("Trade stopped")

def startTrade(request):
    StopTrade(stop=False).save()
    return HttpResponse("Trade started")
