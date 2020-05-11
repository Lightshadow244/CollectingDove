from django.core.management.base import BaseCommand, CommandError
import requests

class Command(BaseCommand):
     def handle(self, *args, **options):
        #self.stdout.write("Unterminated line", ending='')
        response = requests.get("http://api.open-notify.org/iss-now.json")
        # Print the status code of the response.
        print(response.status_code)
