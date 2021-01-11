from django.core.management.base import BaseCommand, CommandError
from twill.commands import *
from twill import set_output, browser
from os import path
from CollectingDove.settings import BASE_DIR
import json
import subprocess
import platform
from io import StringIO

class Command(BaseCommand):
    def add_arguments(self, parser):
    # Positional arguments
        parser.add_argument("value", type=int)

    def handle(self, *args, **options):
        value = options["value"]

        loginData = {}
        if(path.exists(path.join(BASE_DIR, 'website/login.private'),)):
            with open(path.join(BASE_DIR, 'website/login.private')) as json_file:
                loginData = json.load(json_file)
        else:
            print("no login file")

###############################################################################
#fidor Login
###############################################################################

        browser.go("https://auth.fidor.de/session/new")
        fv("1", "session_username", loginData["fidor_login"])
        fv("1", "session_password", loginData["fidor_password"])
        submit()
        info()
        print(browser.showforms())
###############################################################################
#Bitcoin Login
###############################################################################

        go("https://www.bitcoin.de/de/create_reservation")
        
        if(browser.code is 200):
            fv("1", "username", loginData["bitcoin_login"])
            fv("1", "password", loginData["bitcoin_password"])
            #print(browser.showforms())
            submit("0")
        else:
            raise Exception("BTC Login page not loaded")
        
        if(browser.code is 200):
            password2 = subprocess.check_output(["oathtool", "-b", "--totp", loginData["bitcoin_password2"]]).decode("utf-8")
            fv("1", "login_otp[otp]", password2[:6])
            #print(browser.showforms())
            submit("0")
        else:
            raise Exception("BTC Login failed")
        
        if(browser.code is 200):
            fv("1", "reservation_amount_5000", True)
            fv("1", "reservation_period_1", True)
            
            #fv("1", "reservation_amount_custom", True)
            #fv("1", "custom_amount_input", str(value))
            #print(browser.showforms())
            form = browser.form("1")
            valueField = browser.form_field(form,"reservation_amount_5000")
            valueField.value = str(value)
            #submit("0")
        else:
            raise Exception("BTC OTP failed")
        #print(browser.code)
        #print(browser.html)
        
        
