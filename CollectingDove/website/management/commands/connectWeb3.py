from django.core.management.base import BaseCommand, CommandError
from os import path
from CollectingDove.settings import BASE_DIR
import json, subprocess, sys, gammu, time
#import subprocess
from selenium import webdriver 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
#import sys
#import gammu
#imoprt time

class Command(BaseCommand):
    def add_arguments(self, parser):
    # Positional arguments
        parser.add_argument("value", type=int,nargs='?', default=100)

    def handle(self, *args, **options):
        value = str(options["value"])

        loginData = {}
        if(path.exists(path.join(BASE_DIR, 'website/login.private'),)):
            with open(path.join(BASE_DIR, 'website/login.private')) as json_file:
                loginData = json.load(json_file)
        else:
            print("no login file")

###############################################################################
#check SMS Device
###############################################################################

        print("check SMS Device")
        sm = gammu.StateMachine()
        sm.ReadConfig()
        sm.Init()

###############################################################################
#Bitcoin Login
###############################################################################
        driver = webdriver.Chrome()  # Optional argument, if not specified will search path.
        driver.get('https://www.bitcoin.de/de/create_reservation')

        print("fill login form")

        try:
            driver.find_element_by_id('login_username').send_keys(loginData["bitcoin_login"])
            driver.find_element_by_id('login_password').send_keys(loginData["bitcoin_password"])
            driver.find_element_by_id('signin_button').click()
        except Exception as e :
            print(e)
            driver.save_screenshot("../tmp/error.png")
            sys.exit(0)

        print("fill oath form")

        oath = subprocess.check_output(["oathtool", "-b", "--totp", loginData["bitcoin_password2"]]).decode("utf-8")

        try:
            driver.find_element_by_id('login_otp_otp').send_keys(oath[:6])
            driver.find_element_by_id('signin_button').click()
        except Exception as e :
            print(e)
            driver.save_screenshot("../tmp/error.png")
            sys.exit(0)

        print("fill reservation form")
        cancleReservation = driver.find_elements_by_xpath("//*[contains(text(), 'Reservierung aufheben')]")
        deleteReservation = driver.find_elements_by_xpath("//*[contains(text(), 'aufheben')]")
        if(len(cancleReservation) != 0):
            cancleReservation[0].click()
        elif(len(deleteReservation) != 0):
            deleteReservation[0].click()

        try:
            driver.find_element_by_id('reservation_amount_100000').send_keys(Keys.DOWN)

            driver.find_element_by_id('custom_amount_input').send_keys(value)

            driver.find_element_by_id('reservation_period_custom').send_keys(Keys.UP)
            driver.find_element_by_id('reservation_period_1').send_keys(Keys.ENTER)
        except Exception as e :
            print(e)
            driver.save_screenshot("../tmp/error.png")
            sys.exit(0)

###############################################################################
#Fidor Login
###############################################################################
        print("Fidor Login")
        try:
            driver.find_element_by_id('session_username').send_keys(loginData["fidor_login"])
            driver.find_element_by_id('session_password').send_keys(loginData["fidor_password"])
            driver.find_element_by_id('session_password').send_keys(Keys.ENTER)
        except Exception as e :
            print(e)
            driver.save_screenshot("../tmp/error.png")
            sys.exit(0)

###############################################################################
#Fidor Login TAN
###############################################################################

        print("Fidor Login Tan")
        remain = sm.GetSMSStatus()['SIMUsed']
        count = 0
        tan = ""
        while(remain == sm.GetSMSStatus()['SIMUsed']):
            count += 1
            if(count > 30):
                raise Exception("Timeout: no new sms")
            time.sleep(5)

        try:
            sms = sm.GetSMS(Location=remain+1,Folder=0)[0]
            tan = sms['Text'][sms['Text'].find(":")+2:]
            print(tan)
        except gammu.ERR_EMPTY:
            raise Exception("Failed to read SMS")

        try:
            driver.find_element_by_id('northbound_action_otp').send_keys(tan)
            driver.find_element_by_id('northbound_action_otp').send_keys(Keys.ENTER)

            driver.find_element_by_id('tan_submit').click()
        except Exception as e :
            print(e)
            driver.save_screenshot("../tmp/error.png")
            sys.exit(0)

###############################################################################
#Fidor mTAN
###############################################################################

        print("Fidor mTan")
        remain = sm.GetSMSStatus()['SIMUsed']
        count = 0
        tan = ""
        while(remain == sm.GetSMSStatus()['SIMUsed']):
            count += 1
            if(count > 30):
                raise Exception("Timeout: no new sms")
            time.sleep(5)

        try:
            sms = sm.GetSMS(Location=remain+1,Folder=0)[0]
            tan = sms['Text'][sms['Text'].find(":")+2:]
            print(tan)
        except gammu.ERR_EMPTY:
            raise Exception("Failed to read SMS")

        try:
            driver.find_element_by_id('tan').send_keys(tan)
            driver.find_element_by_id('tan').send_keys(Keys.ENTER)
        except Exception as e :
            print(e)
            driver.save_screenshot("../tmp/error.png")
            sys.exit(0)

        driver.save_screenshot("../tmp/success.png")
        print("success")

        driver.quit()
        


#driver.execute_script("scroll(0, 250)")
#driver.find_element_by_xpath("//label[@for='reservation_amount_custom']").click()
 #e.send_keys(Keys.TAB)
            #for x in range(7):
            #    e.send_keys(Keys.DOWN)