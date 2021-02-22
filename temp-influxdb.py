#!/usr/bin/env python
# Python 3, prerequis : pip install pySerial influxdb



import serial
import time
import logging
import requests
from datetime import datetime
from influxdb import InfluxDBClient

# création du logguer
logging.basicConfig(filename='/home/pi/data/log/temp-influxdb.log', level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger()

# connexion a la base de données InfluxDB
client = InfluxDBClient('localhost', 8086)
db = "homedata"
connected = False
while not connected:
    try:
        # print ("Database %s exists?", db)
        if not {'name': db} in client.get_list_database():
            # print ("Database %s creation..", db)
            client.create_database(db)
            # print ("Database %s created!", db)
        client.switch_database(db)
        logging.warn('Connected to the influx database')
        # print ("Connected to ", db)
    except requests.exceptions.ConnectionError:
        logging.warn('InfluxDB is not reachable. Waiting 5 seconds to retry.')
        time.sleep(5)
    else:
        connected = True


def add_measures(temp):
    points = []
    point = {
                "measurement": "temperature",
                "tags": {
                    "host": "raspberry",
                    "location": "exterieur"
                },
                "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "fields": {
                    "value": temp
                }
            }
    # print ("Database point ", point)
    points.append(point)

    client.write_points(points)
    logging.info("New temp value %s for location %s", temp, "exterieur")

def lireFichier (emplacement) :
    # Ouverture du fichier contenant la temperature
    fichTemp = open(emplacement)
    # Lecture du fichier
    contenu = fichTemp.read()
    # Fermeture du fichier apres qu'il ai ete lu
    fichTemp.close()
    return contenu

def recupTemp (contenuFich) :
    # Supprimer la premiere ligne qui est inutile
    secondeLigne = contenuFich.split("\n")[1]
    temperatureData = secondeLigne.split(" ")[9]
    # Supprimer le "t="
    temperature = float(temperatureData[2:])
    # Mettre un chiffre apres la virgule
    temperature = temperature / 1000
    return temperature

contenuFich = lireFichier("/sys/bus/w1/devices/28-0119124f3922/w1_slave")
temperature = recupTemp (contenuFich)

# insertion dans influxdb
add_measures(temperature)

# result = client.query('select value from temp;')

# print("Result: {0}".format(result))
