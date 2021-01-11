from django.core.management.base import BaseCommand, CommandError
from os import path
from CollectingDove.settings import BASE_DIR
import json
import subprocess
import mechanize
from twill import browser

class Command(BaseCommand):
    def add_arguments(self, parser):
    # Positional arguments
        parser.add_argument("value", type=int)

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
        br = mechanize.Browser()
        br.set_handle_robots(False)
        br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

        response = br.open('https://www.bitcoin.de/de/create_reservation')

        br.select_form(nr=0)
        br.form['login[username]'] = loginData["bitcoin_login"]
        br.form['login[password]'] = loginData["bitcoin_password"]
        br.submit()

        password2 = subprocess.check_output(["oathtool", "-b", "--totp", loginData["bitcoin_password2"]]).decode("utf-8")
        br.select_form(nr=0)
        br.form['login_otp[otp]'] = password2[:6]
        br.submit()

        br.select_form(nr=0)
        br.form['reservation[period]'] = ['1']

        br.form.find_control(nr=1).items[0].attrs['value'] = value
        print(br.form.find_control(nr=1).items)
        br.form['reservation[amount]'] = ['100']

        br.submit()


        print(br.response().read())

        for f in br.forms():
            print(f)
        
