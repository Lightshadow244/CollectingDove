from django.core.management.base import BaseCommand, CommandError
from website.models import StopTrade

class Command(BaseCommand):
    def handle(self, *args, **options):
        StopTrade(stop=False).save()
        print('Trade start')
