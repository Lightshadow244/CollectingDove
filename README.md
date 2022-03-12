# CollectingDove
What will the dove collect?

An Environment to trade Bitcoins daily on Bitcoin.de. A Cronjob execute the command "trade" under CollectingDove/website/management/commands/ every 5 minutes. The Webpage shows the details of the past trades.
  
# Installation
install virtualenv  
`apt-get install python-virtualenv`  
`virtualenv -p /usr/bin/python3 ENV`  
`source /home/user/ENV/bin/activate` 

install oathtool - one time password  
`sudo apt install oathtool`

xvfb - run selenium in background
`apt install xvfb`

update pip  
`pip install --upgrade pip`

install rquirements(Dajngo, eyeD3,...)  
`pip install -r CollectionDove/requirements.txt`

do some Django Magic  
`python manage.py makemigrations`  
`python manage.py migrate`

start server  
`python ownmusicweb/manage.py runserver 0.0.0.0:8000`

# Gammu
`apt install gammu libgammu-dev` 
Not necessary anymore
`pip install python-gammu`
