# CollectingDove
What will the dove collect?

An Environment to trade Bitcoins daily on Bitcoinn.de. A Cronjob execute the command "trade" under CollectingDove/website/management/commands/ every 5 minutes.
  
# Installation
install virtualenv  
`apt-get install python-virtualenv`  
`virtualenv -p /usr/bin/python3 ENV`  
`source /home/user/ENV/bin/activate` 

install oathtool  
`sudo apt install oathtool`

update pip  
`pip install --upgrade pip`

install rquirements(Dajngo, eyeD3,...)  
`pip install -r CollectionDove/requirements.txt`

do some pyhton Magic  
`python manage.py makemigrations`  
`python manage.py migrate`

start server  
`python ownmusicweb/manage.py runserver 0.0.0.0:8000`


# Gammu
`apt install gammu libgammu-dev`  
`pip install python-gammu`
