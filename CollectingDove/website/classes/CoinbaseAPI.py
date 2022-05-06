from wsgiref.headers import Headers
from CollectingDove.settings import BASE_DIR
from os import path
import json, time, hashlib, requests, hmac
from django.core import serializers


class CoinbaseAPI:
    def __init__(self):
        self.logLevel = 0

        if(path.exists(path.join(BASE_DIR, 'website/coinbase_apikey.private'),)):
            with open(path.join(BASE_DIR, 'website/coinbase_apikey.private')) as json_file:
                self.cred = json.load(json_file)
        else:
            raise Exception("no api credentials were given")

        self.key = self.cred['key']
        self.secret = self.cred['secret']
        self.basePath = "https://api.coinbase.com"

        pMs = self.getPaymentMethods()
        for pM in pMs:
            if pM["name"] == "EUR Wallet":
                self.paymentMethod = pM
        
        self.accounts = self.getAccount()

        for a in self.accounts:
            if a["name"] == "Euro Wallet":
                self.accountEurId = a["id"]
            elif a["name"] == "BTC Wallet":
                self.accountBtcId = a["id"]
        
    
    def getAccount(self):
        self.log("readAccount")
        
        path = "/v2/accounts"
        url = self.basePath + path

        method = "GET"
        body = ""
        
        headers = self.returnSignedHeaders(method, body, path)

        data = {}
        self.log(url)
        response = requests.get(url, headers=headers)
        if(response is not None):
            if(response.status_code == 200):
                data = response.json()['data']
                self.log("response")
                self.logJson(data)
            else:
                print(response.json())
                raise Exception("http status != 200")

        return(data)

    def getPrice(self, buyBtc):
        self.log("price")

        type = ""
        if buyBtc:
            type = "buy"
        else:
            type = "sell"
        
        path = "/v2/prices/BTC-EUR/"
        url = self.basePath + path + type

        method = "GET"
        body = ""
        
        headers = self.returnSignedHeaders(method, body, path)

        data = {}
        self.log(url)
        response = requests.get(url, headers=headers)
        if(response is not None):    
            if(response.status_code == 200):
                data = response.json()['data']
                self.log("response")
                self.logJson(data)
            else:
                print(response.json())
                raise Exception("http status != 200")
        return(data)

    def getPaymentMethods(self):
        self.log("getPaymentMethods")
        
        path = "/v2/payment-methods"
        url = self.basePath + path

        method = "GET"
        body = ""
        
        headers = self.returnSignedHeaders(method, body, path)

        data = {}
        self.log(url)
        response = requests.get(url, headers=headers)
        if(response is not None):
            if(response.status_code == 200):
                data = response.json()['data']
                self.log("response")
                self.logJson(data)
            else:
                print(response.json())
                raise Exception("http status != 200")

        return(data)

    def postBuy(self, totalAmount):
        self.log("postBuy")
        
        path = "/v2/accounts/" + self.accountBtcId + "/buys"
        url = self.basePath + path

        method = "POST"
        body = {
            "currency": "EUR",
            "total": str(totalAmount),
            "payment_method": self.paymentMethod["id"]
        }
        
        headers = self.returnSignedHeaders(method, json.dumps(body), path)

        data = {}
        self.log(url)
        response = requests.post(url, headers=headers, data=json.dumps(body))
        if(response is not None):
            if(response.status_code in {200,201}):
                data = response.json()['data']
                self.log("response")
                self.logJson(data)
            else:
                print(response.json())
                raise Exception("http status != 200")

        return(data)

    def postSell(self, totalAmount):
        self.log("postSell")
        
        path = "/v2/accounts/" + self.accountBtcId + "/sells"
        url = self.basePath + path

        method = "POST"
        body = {
            "currency": "BTC",
            "amount": str(totalAmount),
            "payment_method": self.paymentMethod["id"]
        }
        
        headers = self.returnSignedHeaders(method, json.dumps(body), path)

        data = {}
        self.log(url)
        response = requests.post(url, headers=headers, data=json.dumps(body))
        if(response is not None):
            if(response.status_code in {200,201}):
                data = response.json()['data']
                self.log("response")
                self.logJson(data)
            else:
                print(response.json())
                raise Exception("http status != 200")

        return(data)

    def returnSignedHeaders(self, method, body, path):
        timestamp = str(int(time.time()))
        sign = timestamp + method + path + body

        self.log(sign)
        
        hashedSign = hmac.new(self.secret.encode(), sign.encode(), hashlib.sha256).hexdigest()
        self.log(hashedSign)

        headers = {
        "CB-ACCESS-KEY":self.key,
        "CB-ACCESS-SIGN":hashedSign,
        "CB-ACCESS-TIMESTAMP":timestamp
        }
        return headers

    
    def logJson(self, j):
        if self.logLevel == 1:
            print(json.dumps(j, indent=2, sort_keys=True))
    
    def logObject(self, o):
        arr = [o]
        print(serializers.serialize("json", arr))

    def log(self, s):
        if self.logLevel == 1:
            print(s)

    
