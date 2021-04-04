from website.classes.Trade import Trade
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        t = Trade()
        print(t.status)
        print(t.orders[0])