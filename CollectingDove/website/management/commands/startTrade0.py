from django.core.management.base import BaseCommand, CommandError
from website.models import StopTrade

class Command(BaseCommand):
    def handle(self, *args, **options):
        StopTrade(stop=True).save()
        print('Trade stop')
