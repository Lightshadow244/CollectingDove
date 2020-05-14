from django.db import models
from datetime import datetime
from django.utils import timezone

"""for django API
from website.models import Trade_BTC_test
from datetime import datetime, timezone, timedelta
t = Trade_BTC_small(time=(datetime.now()-timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),rate=2.2,btc=3.0,eur=-200.11,eur_to_btc=True)
t = Trade_BTC_small(time=(datetime.now()-timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),rate=2.2)
"""

# Create your models hertime=
class Trade_BTC(models.Model):
    time = models.DateTimeField(default=timezone.now, blank=False)
    rate = models.FloatField(blank=False)
    btc = models.FloatField(blank=True, null=True)
    eur = models.FloatField(blank=True, null=True)
    eur_to_btc = models.BooleanField(blank=True, null=True)

class Trade_BTC_small(Trade_BTC):
    pass

class Trade_BTC_medium(Trade_BTC):
    pass

class Trade_BTC_large(Trade_BTC):
    pass

class Trade_BTC_test(models.Model):
    time = models.DateTimeField(default=timezone.now, blank=False)
    rate = models.FloatField(blank=False)
    btc = models.FloatField(blank=True, null=True)
    eur = models.FloatField(blank=True, null=True)
    eur_to_btc = models.BooleanField(blank=True, null=True)

class Total_Value(models.Model):
    time = models.DateTimeField(default=timezone.now)
    btc = models.FloatField(blank=True, null=True)
    eur = models.FloatField(blank=True, null=True)

class Total_Value_Test(Total_Value):
    pass

class StopTrade(models.Model):
    time = models.DateTimeField(default=timezone.now)
    stop = models.BooleanField(default=True)
