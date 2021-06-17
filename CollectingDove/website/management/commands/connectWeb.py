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
        subprocess.check_output(["gammu", "--deleteallsms" , "1"])
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
        new_sms = 0
        sms = ""
        count = 0 

        while(new_sms == 0):
            if(count > 6):
                driver.save_screenshot("../tmp/error.png")
                raise Exception("Timeout: no new sms")

            print("loop")
            count += 1
            time.sleep(10)

            try:
                sms = subprocess.check_output(["gammu", "--getallsms"]).decode("utf-8")
            except:
                print("fail")
                pass
            if(sms.find("Status") != -1 and sms.find("TAN") != -1):
                new_sms = 1 
        
        tan = sms[sms.find("TAN")+12:sms.find("TAN")+18]
        subprocess.check_output(["gammu", "--deleteallsms" , "1"])
        print(tan)

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
        new_sms = 0
        sms = ""
        count = 0 

        while(new_sms == 0):
            if(count > 6):
                driver.save_screenshot("../tmp/error.png")
                raise Exception("Timeout: no new sms")

            print("loop")
            count += 1
            time.sleep(10)

            try:
                sms = subprocess.check_output(["gammu", "--getallsms"]).decode("utf-8")
            except:
                print("fail")
                pass
            if(sms.find("Status") != -1 and sms.find("TAN") != -1):
                new_sms = 1 
        
        tan = sms[sms.find("TAN")+12:sms.find("TAN")+18]
        subprocess.check_output(["gammu", "--deleteallsms" , "1"])
        print(tan)

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