from django.http import HttpResponse
from website.models import Trade_BTC_test
import csv


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def exportValue(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    writer.writerow(['time', 'rate', 'eur', 'btc'])

    for trade in Trade_BTC_test.objects.order_by('time'):
        writer.writerow([trade.time, trade.rate, trade.eur, trade.btc])

    return response
