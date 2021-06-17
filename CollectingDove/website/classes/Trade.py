from os import path
from CollectingDove.settings import BASE_DIR
from website.models import Trade_BTC, Total_Value, StopTrade, Counter
from datetime import datetime, timedelta
from django.utils import timezone
import requests, random, json, time, hashlib, hmac, time, collections, subprocess, sys
from selenium import webdriver 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class Trade:
    def __init__(self):
        
        if(StopTrade.objects.order_by('time').last().stop == True or StopTrade.objects.order_by('time').last().stop == None):
            raise Exception("Trading is stopped")
        
        # 0 - off, 1 - on
        self.logLevel = 1

        if(path.exists(path.join(BASE_DIR, 'website/apikey.private'),)):
            with open(path.join(BASE_DIR, 'website/apikey.private')) as json_file:
                self.api = json.load(json_file)
        else:
            raise Exception("no api credentials were given")

        
        if(path.exists(path.join(BASE_DIR, 'website/login.private'),)):
            with open(path.join(BASE_DIR, 'website/login.private')) as json_file:
                self.loginData = json.load(json_file)
        else:
            raise Exception("no credentials to reserve")

        self.status = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S") + ','
        self.lastTrade = Trade_BTC.objects.exclude(btc = None, eur = None).order_by('time').last()
        
        if(self.lastTrade == None):
            raise Exception("DB is empty")

        self.lastValue = Total_Value.objects.order_by('time').last()

        if(self.lastValue == None or (self.lastValue.btc == 0.0 and self.lastValue.eur == 0.0)):
            raise Exception("no start value given")

        self.eurToBtc = self.lastTrade.eur_to_btc
        self.lastRate = Trade_BTC.objects.order_by('time').last()
        self.orders = self.getOrders()

        self.tradeList = []
        self.finishedTrades = []

    def getOrders(self):
        getParameterJson = {'order_requirements_fullfilled': str(1)}
        if(self.lastTrade is None):
            getParameterJson['type'] = 'sell'
        elif(self.lastTrade.eur_to_btc):
            getParameterJson['type'] = 'sell'
        else:
            getParameterJson['type'] = 'buy'
        
        getParameter = ''
        postParameter = ''
        nonce = str(int(time.time()))
        http_method = 'GET'
        uri = 'https://api.bitcoin.de/v4/btceur/orderbook'

        for i, (k,v) in enumerate(getParameterJson.items()):
            if(i == 0):
                getParameter = k + '=' + v
            else:
                getParameter = getParameter + '&' + k + '=' + v

        uri = uri + '?' + getParameter

        self.log(uri)

        md5Post = str(hashlib.md5(postParameter.encode()).hexdigest())

        signatur = http_method + '#' + uri + '#' + self.api['key'] + '#' + nonce + '#' + md5Post
        hashedSignatur = hmac.new(self.api['secret'].encode(), signatur.encode(), hashlib.sha256)

        header = {
        'X-API-KEY':self.api['key'],
        'X-API-NONCE':nonce,
        'X-API-SIGNATURE':hashedSignatur.hexdigest()
        }
        response = requests.get(uri, headers=header)
        if(response is not None):
            if(response.status_code == 200):
                data = response.json()['orders']
        r = sorted(data, key = lambda i: i['price'])

        return(r)

    def isTradeProfitable(self):
        r = False
        if(self.eurToBtc):
            self.status += 'BtcToEur,'
            rate = self.orders[-1]['price']
            deltaTradeRate = self.lastTrade.rate - float(rate)
            deltaRate = self.lastRate.rate - float(rate)
            self.status += str(self.lastTrade.rate) + ',' + str(rate) + ','
            #debugText += 'dtr: ' + str(deltaTradeRate) + ', dr: ' + str(deltaRate) + ','

            newRate = Trade_BTC(rate=rate)

            if(deltaTradeRate < -75 and deltaTradeRate > self.lastRate.highest_peak * 0.9):
            #if(True):
                self.status += '1,'
                r = True
            elif(deltaTradeRate < self.lastRate.highest_peak):
                newRate.highest_peak = deltaTradeRate
                newRate.save()
                self.status += '2,'
            else:
                newRate.highest_peak = self.lastRate.highest_peak
                newRate.save()
                self.status += '3,'
        else:
            self.status += 'EurToBtc,'
            rate = self.orders[0]['price']
            deltaTradeRate = self.lastTrade.rate - float(rate)
            deltaRate = self.lastRate.rate - float(rate)
            self.status += str(self.lastTrade.rate) + ',' + str(rate) + ','
            #debugText += 'dtr: ' + str(deltaTradeRate) + ', dr: ' + str(deltaRate) + ','

            newRate = Trade_BTC(rate=rate)

            if(deltaTradeRate > 75 and deltaTradeRate < self.lastRate.highest_peak * 0.9):
            #if(True):
                self.status += '1,'
                r = True
            elif(deltaTradeRate > self.lastRate.highest_peak):
                newRate.highest_peak = deltaTradeRate
                newRate.save()
                self.status += '2,'
            else:
                newRate.highest_peak = self.lastRate.highest_peak
                newRate.save()
                self.status += '3,'

        if(r == False):
            self.status += 'tradeNotProfitable'

        self.log('peak=' + str(self.lastRate.highest_peak))
        self.log('peak*0.9=' + str(self.lastRate.highest_peak * 0.9))
        self.log('delta=' + str(deltaTradeRate))
        return(r)


    def getTradeOrders(self):
        if(self.eurToBtc):
            counter = -1
            while(abs(counter) <= len(self.orders)):
                trade = {}
                order = self.orders[counter]
                if(float(order['min_amount_currency_to_trade']) <= self.lastValue.btc):
                    if(float(order['max_amount_currency_to_trade']) > self.lastValue.btc):
                        sellBtc = self.lastValue.btc
                        buyEur = sellBtc * float(order['price'])
                        counter = len(self.orders)
                    else:
                        buyEur = float(order['max_volume_currency_to_pay'])
                        sellBtc = float(order['max_amount_currency_to_trade'])
                    #lastValue.btc = lastValue.btc - sellBtc
                    trade['price'] = order['price']
                    trade['order_id'] = order['order_id']
                    trade['btc'] = float(str(sellBtc)[:10])
                    trade['eur'] = buyEur
                    self.tradeList.append(trade)
                counter = counter - 1
        else:
            counter = 0
            while(counter < len(self.orders)):
                trade = {}
                order = self.orders[counter]
                if(float(order['min_volume_currency_to_pay']) <= self.lastValue.eur):
                    if(float(order['max_volume_currency_to_pay']) > self.lastValue.eur):
                        sellEur = self.lastValue.eur
                        buyBtc = sellEur / float(order['price'])
                        counter = len(self.orders)
                    else:
                        buyBtc = float(order['max_amount_currency_to_trade'])
                        sellEur = float(order['max_volume_currency_to_pay'])
                    #self.lastValue.eur = lastValue.eur - sellEur
                    trade['price'] = order['price']
                    trade['order_id'] = order['order_id']
                    trade['btc'] = float(str(buyBtc)[:10])
                    trade['eur'] = sellEur
                    self.tradeList.append(trade)
                counter = counter + 1
        self.log(self.tradeList)

    def executeTrade(self):
        r = []
        postParameterJson = {}
        postParameter = ''
        http_method = 'POST'
        internal_trade_id = int(time.time())


        if(self.eurToBtc):
            for trade in self.tradeList:
                nonce = str(int(time.time()))
                returnTradeInfo = {}
                uri = 'https://api.bitcoin.de/v4/btceur/trades/'
                postParameterJson['amount_currency_to_trade'] = trade['btc']
                postParameterJson['type'] = 'sell'
                postParameterJson = collections.OrderedDict(sorted(postParameterJson.items()))

                for i, (k,v) in enumerate(postParameterJson.items()):
                    if(i == 0):
                        postParameter = k + '=' + str(v)
                    else:
                        postParameter = postParameter + '&' + k + '=' + str(v)

                uri = uri + trade['order_id']


                md5Post = str(hashlib.md5(postParameter.encode()).hexdigest())

                signatur = http_method + '#' + uri + '#' + self.api['key'] + '#' + nonce + '#' + md5Post
                hashedSignatur = hmac.new(self.api['secret'].encode(), signatur.encode(), hashlib.sha256)

                header = {
                'X-API-KEY':self.api['key'],
                'X-API-NONCE':nonce,
                'X-API-SIGNATURE':hashedSignatur.hexdigest()
                }

                response = requests.post(uri, headers=header, data=postParameterJson)

                if(response is not None):
                    returnTradeInfo['status_code'] = response.status_code
                    returnTradeInfo['order_id']  = trade['order_id']
                    returnTradeInfo['type']  = postParameterJson['type']
                    returnTradeInfo['btc'] =    trade['btc']
                    returnTradeInfo['price'] = trade['price']
                    returnTradeInfo['eur'] =    trade['eur'] * 0,995
                    self.finishedTrades.append(returnTradeInfo)
                    if(response.status_code == 201):
                        newTrade = Trade_BTC(rate=trade['price'],eur=trade['eur'],btc=trade['btc']  * -1, eur_to_btc=False, internal_trade_id=internal_trade_id)
                        newTrade.save()
                        newValue = Total_Value(eur=Total_Value.objects.order_by('time').last().eur + returnTradeInfo['eur'],btc=Total_Value.objects.order_by('time').last().btc - returnTradeInfo['btc'])
                        newValue.save()
                    else:
                        raise Exception(response.json())
        else:
            for trade in self.tradeList:
                nonce = str(int(time.time()))
                returnTradeInfo = {}
                uri = 'https://api.bitcoin.de/v4/btceur/trades/'
                postParameterJson['amount_currency_to_trade'] = trade['btc']
                postParameterJson['type'] = 'buy'
                postParameterJson = collections.OrderedDict(sorted(postParameterJson.items()))



                for i, (k,v) in enumerate(postParameterJson.items()):
                    if(i == 0):
                        postParameter = k + '=' + str(v)
                    else:
                        postParameter = postParameter + '&' + k + '=' + str(v)

                uri = uri + str(trade['order_id'])

                md5Post = str(hashlib.md5(postParameter.encode()).hexdigest())

                signatur = http_method + '#' + uri + '#' + self.api['key'] + '#' + nonce + '#' + md5Post
                hashedSignatur = hmac.new(self.api['secret'].encode(), signatur.encode(), hashlib.sha256)

                header = {
                'X-API-KEY':self.api['key'],
                'X-API-NONCE':nonce,
                'X-API-SIGNATURE':hashedSignatur.hexdigest()
                }
                    
                response = requests.post(uri, headers=header, data=postParameterJson)
                
                if(response is not None):
                    returnTradeInfo['status_code'] = response.status_code
                    returnTradeInfo['order_id']  = trade['order_id']
                    returnTradeInfo['type']  = postParameterJson['type']
                    returnTradeInfo['btc'] =    trade['btc'] * 0,995
                    returnTradeInfo['price'] = trade['price']
                    returnTradeInfo['eur'] =    trade['eur']
                    self.finishedTrades.append(returnTradeInfo)
                    if(response.status_code == 201):
                        newTrade = Trade_BTC(rate=trade['price'],eur=trade['eur'] * -1,btc=trade['btc'], eur_to_btc=True, internal_trade_id=internal_trade_id)
                        newTrade.save()
                        newValue = Total_Value(eur=Total_Value.objects.order_by('time').last().eur - trade['eur'],btc=Total_Value.objects.order_by('time').last().btc + trade['btc'])
                        newValue.save()
                    else:
                        self.log(response.json())

        if(len(self.finishedTrades) > 0):
            self.status += self.finishedTrades[0]['type']

        for trade in self.finishedTrades:
            self.status += str(trade['order_id']) + str(trade['price']) + str(trade['eur']) + str(trade['btc'])

    def reserveValue(self):

###############################################################################
#Bitcoin Login
###############################################################################
        driver = webdriver.Chrome()  # Optional argument, if not specified will search path.
        driver.get('https://www.bitcoin.de/de/create_reservation')

        self.log("fill login form")

        try:
            driver.find_element_by_id('login_username').send_keys(self.loginData["bitcoin_login"])
            driver.find_element_by_id('login_password').send_keys(self.loginData["bitcoin_password"])
            driver.find_element_by_id('signin_button').click()
        except Exception as e :
            print(e)
            driver.save_screenshot("../tmp/error.png")
            sys.exit(0)

        self.log("fill oath form")

        oath = subprocess.check_output(["oathtool", "-b", "--totp", self.loginData["bitcoin_password2"]]).decode("utf-8")

        try:
            driver.find_element_by_id('login_otp_otp').send_keys(oath[:6])
            driver.find_element_by_id('signin_button').click()
        except Exception as e :
            print(e)
            driver.save_screenshot("../tmp/error.png")
            sys.exit(0)

        self.log("fill reservation form")
        cancleReservation = driver.find_elements_by_xpath("//*[contains(text(), 'Reservierung aufheben')]")
        deleteReservation = driver.find_elements_by_xpath("//*[contains(text(), 'aufheben')]")
        if(len(cancleReservation) != 0):
            cancleReservation[0].click()
        elif(len(deleteReservation) != 0):
            deleteReservation[0].click()

        try:
            driver.find_element_by_id('reservation_amount_100000').send_keys(Keys.DOWN)
            driver.find_element_by_id('custom_amount_input').send_keys(int(self.lastValue.eur))

            driver.find_element_by_id('reservation_period_custom').send_keys(Keys.UP)
            driver.find_element_by_id('reservation_period_1').send_keys(Keys.ENTER)
        except Exception as e :
            print(e)
            driver.save_screenshot("../tmp/error.png")
            sys.exit(0)

###############################################################################
#Fidor Login
###############################################################################
        self.log("Fidor Login")
        subprocess.check_output(["gammu", "--deleteallsms" , "1"])
        try:
            driver.find_element_by_id('session_username').send_keys(self.loginData["fidor_login"])
            driver.find_element_by_id('session_password').send_keys(self.loginData["fidor_password"])
            driver.find_element_by_id('session_password').send_keys(Keys.ENTER)
        except Exception as e :
            print(e)
            driver.save_screenshot("../tmp/error.png")
            sys.exit(0)

###############################################################################
#Fidor Login TAN
###############################################################################
        self.log("Fidor Login Tan") 
        new_sms = 0
        sms = ""
        count = 0 

        while(new_sms == 0):
            if(count > 6):
                driver.save_screenshot("../tmp/error.png")
                raise Exception("Timeout: no new sms")

            self.log("loop")
            count += 1
            time.sleep(10)

            try:
                sms = subprocess.check_output(["gammu", "--getallsms"]).decode("utf-8")
            except:
                self.log("fail")
                pass
            if(sms.find("Status") != -1 and sms.find("TAN") != -1):
                new_sms = 1 
        
        tan = sms[sms.find("TAN")+12:sms.find("TAN")+18]
        subprocess.check_output(["gammu", "--deleteallsms" , "1"])
        self.log(tan)

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

        self.log("Fidor mTan")
        new_sms = 0
        sms = ""
        count = 0 

        while(new_sms == 0):
            if(count > 6):
                driver.save_screenshot("../tmp/error.png")
                raise Exception("Timeout: no new sms")

            self.log("loop")
            count += 1
            time.sleep(10)

            try:
                sms = subprocess.check_output(["gammu", "--getallsms"]).decode("utf-8")
            except:
                self.log("fail")
                pass
            if(sms.find("Status") != -1 and sms.find("TAN") != -1):
                new_sms = 1 
        
        tan = sms[sms.find("TAN")+12:sms.find("TAN")+18]
        subprocess.check_output(["gammu", "--deleteallsms" , "1"])
        self.log(tan)

        try:
            driver.find_element_by_id('tan').send_keys(tan)
            driver.find_element_by_id('tan').send_keys(Keys.ENTER)
        except Exception as e :
            print(e)
            driver.save_screenshot("../tmp/error.png")
            sys.exit(0)

        driver.save_screenshot("../tmp/success.png")
        self.log("success")

        driver.quit()

    def log(self, s):
        if(self.logLevel == 1):
            print(s)