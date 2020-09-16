from django.shortcuts import render
from django.http import HttpResponse
from website.models import Trade_BTC_test, StopTrade, Trade_BTC
from django.template import loader
import csv
from datetime import datetime, timezone, timedelta


class BlankObj:
    def __repr__(self):
        return ""

def index(request):
    template = loader.get_template('CollectingDove/index.html')

    #letzten zwei Tage 12 DP in einer Stunde * 48 Stunden = 576 Datenpunkte
    #last2d = datetime.now() - timedelta(days=2)
    last2d = datetime(2020,9,13,0,0,0)
    last2d = last2d.replace(tzinfo=timezone.utc)

    rates_2d = Trade_BTC.objects.filter(time__gte=last2d).order_by('time')

    #list_label = []
    list_label = ''
    list_trades = []
    list_rates = []
    t = 0
    for rate in rates_2d:
        # list_trades
        if(rate.btc is None and rate.eur is None ):
            list_trades.append(None)
        else:
            list_trades.append({'rate':rate.rate,'eur':rate.eur,'btc':rate.btc,'eur_to_btc':rate.eur_to_btc,'time':rate.time})

        # list_rates
        list_rates.append(rate.rate)

        # list_label
        if(rate.time.hour > t or (t == 23 and rate.time.hour == 0)):
            t = rate.time.hour
            #list_label.append(t)
            list_label += str(t) + ','
        else:
            list_label += '' + ','
    print(list_label)
    #print('###################')
    #print(list_rates)
    #print('###################')
    #print(list_trades)



    context = {'list_label':list_label,'list_trades':list_trades,'list_rates':list_rates
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
