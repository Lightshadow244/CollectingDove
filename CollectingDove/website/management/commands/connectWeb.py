from django.core.management.base import BaseCommand, CommandError
from twill.commands import *
from os import path
from CollectingDove.settings import BASE_DIR
import json
import subprocess
import platform

class Command(BaseCommand):
    def handle(self, *args, **options):

        loginData = {}
        if(path.exists(path.join(BASE_DIR, 'website/login.private'),)):
            with open(path.join(BASE_DIR, 'website/login.private')) as json_file:
                loginData = json.load(json_file)
        else:
            print("no login file")
###############################################################################
#Bitcoin Login
###############################################################################
        uri = 'https://www.bitcoin.de/de/login'
        header = {}
        postParameterJson = {}

#        response = requests.post(uri, headers=header, data=postParameterJson)
#        if(response is not None):
#            print(response)
#        else:
#            print("wrong")
        go("https://www.bitcoin.de/de/login")
        fv("1", "username", loginData["bitcoin_login"])
        fv("1", "password", loginData["bitcoin_password"])
        submit("0")

        password2 = subprocess.run("oathtool", "-b", "--totp", loginData["bitcoin_password2"])
        showforms()
