from django.db import models
from django.utils import timezone
import time

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
    highest_peak = models.FloatField(default=0.0)
    internal_trade_id = models.IntegerField(blank=True, null=True)

class Total_Value(models.Model):
    time = models.DateTimeField(default=timezone.now)
    btc = models.FloatField(blank=True, null=True)
    eur = models.FloatField(blank=True, null=True)

class StopTrade(models.Model):
    time = models.DateTimeField(default=timezone.now)
    stop = models.BooleanField(default=True)

class Counter(models.Model):
    counter = models.IntegerField(default=0)

class Graph_RatesPerDay(models.Model):
    time = models.DateTimeField(default=timezone.now, blank=False)
    rate = models.FloatField(blank=False)
    trades = models.TextField(blank=True)

class Sms(models.Model):
    time = models.DateTimeField(default=timezone.now, blank=False)
    number = models.CharField(max_length=20)
    text  = models.TextField(blank=True)

class TradeInfoModel(models.Model):
    #time = models.DateTimeField(default=timezone.now, blank=False)
    time = models.CharField(max_length=11,default=str(time.mktime(timezone.now().timetuple()))[:-2], blank=False)
    rate = models.FloatField(blank=False)
    peakRate = models.FloatField(default=0.0)
    buyBtc = models.BooleanField(blank=False)
    shouldTrade = models.BooleanField(default=False)
    btc =  models.FloatField(default=0.0)
    #lastTradeRate = models.FloatField(blank=True, null=True)
    lastTrade = models.BooleanField(default=False)

class CoinbaseTradeModel(models.Model):
    time = models.CharField(max_length=11,default=str(time.mktime(timezone.localtime(timezone.now()).timetuple()))[:-2], blank=False)
    rate = models.FloatField(blank=False)
    peakRate = models.FloatField(default=0.0)
    buyBtc = models.BooleanField(blank=False)
    btc =  models.FloatField(default=0.0)
    eur =  models.FloatField(default=0.0)
    isTrade = models.BooleanField(default=False)
    status = models.CharField(max_length=1, default="3")

class Test(models.Model):
    time = models.CharField(max_length=11)
    value = models.FloatField(default=0.0)

