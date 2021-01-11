from django.core.management.base import BaseCommand, CommandError
from os import path
from CollectingDove.settings import BASE_DIR
import json
import subprocess

class Command(BaseCommand):
    def add_arguments(self, parser):
    # Positional arguments
        parser.add_argument("value", type=int,nargs='?', default=1)

    def handle(self, *args, **options):
        value = str(options["value"])

        loginData = {}
        if(path.exists(path.join(BASE_DIR, 'website/login.private'),)):
            with open(path.join(BASE_DIR, 'website/login.private')) as json_file:
                loginData = json.load(json_file)
        else:
            print("no login file")

###############################################################################
#Bitcoin Login
###############################################################################
        print("test")
        
