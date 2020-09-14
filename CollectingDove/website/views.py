from django.shortcuts import render
from django.http import HttpResponse
from website.models import Trade_BTC_test, StopTrade
import csv


def index(request):
    return render(request, 'CollectingDove/index.html')

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
