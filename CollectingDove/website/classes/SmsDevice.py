import subprocess
from website.models import Sms

class SmsDevice:
    def __init__(self):
        pass

    def getAll(self):
        s = ""
        while(s == ""):
            try:
                s = subprocess.check_output(["gammu", "--getallsms"]).decode("utf-8")
            except:
                print("smsDevice currently not available")
        return(s)
    
    def saveAll(self):
        s = ""
        while(s == ""):
            try:
                s = subprocess.check_output(["gammu", "--getallsms"]).decode("utf-8")
            except:
                print("smsDevice currently not available")
        if(s.find("Remote number") > -1):
            number = s[s.find(":", s.find("Remote number"))+2:s.find("Status")-1]
            text = s[s.find("\n",s.find("Status"))+2:s.find("SMS parts")-5]
            Sms(number=number, text=text).save()

    def deleteSaved(self):
        pass

    def deleteAll():
        subprocess.check_output(["gammu", "--deleteallsms" , "1"])
