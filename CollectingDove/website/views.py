from django.shortcuts import render
from django.http import HttpResponse
from website.models import StopTrade, Trade_BTC, Graph_RatesPerDay
from django.template import loader
import csv
from datetime import datetime, timezone, timedelta
from website.classes.SmsDevice import SmsDevice


class BlankObj:
    def __repr__(self):
        return ""

def index(request):
    template = loader.get_template('CollectingDove/index.html')

    #letzten zwei Tage 12 DP in einer Stunde * 48 Stunden = 576 Datenpunkte
    #last2d = datetime.now() - timedelta(days=2)
    last2d = datetime(2020,9,11,0,0,0)
    last2d = last2d.replace(tzinfo=timezone.utc)

    rates_2d = Graph_RatesPerDay.objects.filter(time__gte=last2d).order_by('time')

    #list_label = []
    list_label = ''
    list_trades = []
    list_rates = ''
    t = 0
    for rate in rates_2d:
        # list_trades
        #if(rate.btc is None and rate.eur is None ):
        #    list_trades.append(None)
        #else:
        #    list_trades.append({'rate':rate.rate,'eur':rate.eur,'btc':rate.btc,'eur_to_btc':rate.eur_to_btc,'time':rate.time})

        # list_rates
        if(len(list_rates) == 0):
            list_rates += str(rate.rate)
        else:
            list_rates += ',' + str(rate.rate)


        # list_label
        #if(rate.time.hour > t or (t == 23 and rate.time.hour == 0)):
        #    t = rate.time.hour
            #list_label.append(t)
        #    list_label += str(t) + ','
        #else:
        #    list_label += '' + ','
        if(len(list_label) == 0):
            list_label += rate.time.strftime("%d.%m.%y")
        else:
            list_label += ',' + rate.time.strftime("%d.%m.%y")
    print(list_label)
    #print('###################')
    #print(list_rates)
    #print('###################')
    #print(list_trades)

    
    s = SmsDevice().getAll()
    sms_list = []
    count_sms = s.count("Remote number")
    start = 0

    while(count_sms > 0):
        start = s.find(":", s.find("Sent", start))
        date = s[start+2:s.find("Coding", start)-7]
        number = s[s.find(":", s.find("Remote number", start))+3:s.find("Status", start)-2]

        if(count_sms > 1):
            text = s[s.find("\n",s.find("Status", start))+2:s.find("Location", start)]
        else:
            text = s[s.find("\n",s.find("Status", start))+2:s.find("SMS parts", start)-5]
        
        sms_list.append(date + ", " + number + ": " + text)
        count_sms -= 1



    context = {'list_label':list_label,'list_trades':list_trades,'list_rates':list_rates,'sms_list':sms_list}
    return HttpResponse(template.render(context, request))

def exportValue(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    writer.writerow(['time', 'rate', 'eur', 'btc'])

    for trade in Trade_BTC.objects.order_by('time'):
        writer.writerow([trade.time, trade.rate, trade.eur, trade.btc])

    return response

def stopTrade(request):
    StopTrade(stop=True).save()
    return HttpResponse("Trade stopped")

def startTrade(request):
    StopTrade(stop=False).save()
    return HttpResponse("Trade started")
