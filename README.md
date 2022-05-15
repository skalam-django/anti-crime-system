# Anti-Crime System

Anti-Crime System: It's IoT based system integrated with Django web application. On a single press of a button(either software or hardware), the system tracks the victim location and alarms the locals with a siren and push notification to the nearby mobile users as well as the police station. It will be very helpful when mobile network is not available at the victim location. 

### Repo owner or admin

Sk Khurshid Alam

### Dependencies
* [**Python**](https://www.python.org/downloads/)
* [**Django**](https://docs.djangoproject.com/en/4.0/)
* [**Celery**](https://docs.celeryq.dev/en/stable/getting-started/introduction.html)
* [**PostgreSQL**](https://www.postgresql.org/download/)
* [**Redis**](https://redis.io/download/)
* [**NodeMCU**](https://nodemcu.readthedocs.io/en/release/)
* [**Ai Thinker LoRa-Ra-01 RF Transceiver Module**](https://www.electronicscomp.com/ai-thinker-lora-ra-01-rf-transceiver-module?gclid=Cj0KCQjwyYKUBhDJARIsAMj9lkEhZzkRhc4-aCUOrKSqQhR5kje3HHtiygVeeFFmT7vdPbt7e18upfoaAnbVEALw_wcB)
* [**GPS Module**](https://www.electronicwings.com/sensors-modules/gps-receiver-module)
* [**SIM800L**](https://lastminuteengineers.com/sim800l-gsm-module-arduino-tutorial/)
* [**Arduino IDE**](https://www.arduino.cc/en/software)

## Setup everything needed to run the server

Install PostgreSQL, you may follow the steps given in this link:
```
https://www.cherryservers.com/blog/how-to-install-and-setup-postgresql-server-on-ubuntu-20-04
```

Install Redis-Server:
```
sudo apt-get install redis-server
```

To start Redis automatically when your server boots:
```
sudo systemctl enable redis
```

Start Redis as Service:
```
sudo systemctl start redis
```


Create Virtual Enviroment:
```
virtualenv -p python3 venv
```

Activate the Virtual Environment:
```
source venv/bin/activate
```

Install Dependecies:
```
pip install -r requirements.txt
```

Create database in your PostgreSQL server:
```
create database acs;
```


Export Enviroment Variables:
```
export SERVER=DEV
export ACS_SECRET_KEY=xq4e*ltvt%&)c8=(s64eo23wj^^!=w61isrpwc3#r9(7qieqp
export ACS_SERVICES=True
export AES128_CPIN=8MDOFMUZYY2G2YVF3YWBIXMS61Z3LV2B
export ACS_NAME=acs
export ACS_USER=postgres
export ACS_PASSWORD=admin@123
export ACS_HOST=localhost
export ACS_PORT=5432
```

Migrate models into database:
```
python manage.py migrate
```

Run Application directly in Linux Terminal:
```
python manage.py runserver
```
**Note:** Change host and port according to your needs.<br/>

Run Celery directly in Linux Terminal:
```
celery -A acs worker -B --loglevel=info
```

## Sample Test
http://localhost:8000



