# LANCEMENT DU SERVICE AU BOOT DU PI 
# /lib/systemd/system/tempServer.service 
# sudo service tempServer status


from http.server import HTTPServer, BaseHTTPRequestHandler

import serial
import time
import logging
import requests
from datetime import datetime
from influxdb import InfluxDBClient
from io import BytesIO
import simplejson



# création du logguer
logging.basicConfig(filename='/var/log/tempServer.log', level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger()


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        logging.info("test GET ")
        # client.drop_database(db)
        self.wfile.write(b'Test GET')

    def do_POST(self):
        try:
            path= self.path
            logging.debug("Path %s", path)
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            self.send_response(200)
            self.end_headers()
            response = BytesIO()
            
            logging.debug("Body %s", body)
            data = simplejson.loads(body)
            if (path == "/generic") :
                # {"location":"growlab","table":[{"key":"temperature","value":"23"},{"key":"humidity","value":"81.90"}]}
                for x in data['table']:
                    add_measures(x['key'], float(x['value']), data['location'])

            else :
                # {"temperature": "23.00" , "humidity": "81.90", "location": "chambre_emma"}
                add_measures('temperature', float(data['temperature']), data['location'])
                add_measures('humidity', float(data['humidity']), data['location'])
                
            response.write(b'This is POST request.Received: ')
            logging.info("Request on path %s from %s ", path, data['location'])
            logging.debug("Request %s", body)
            response.write(body)
            self.wfile.write(response.getvalue())
        except Exception as e:
            logging.error("Error: {}".format(e))


httpd = HTTPServer(('0.0.0.0', 5000), SimpleHTTPRequestHandler)


def add_measures(key, value, location):
    points = []
    
    point = {
                "measurement": key,
                "tags": {
                    "host": "ESP8266",
                    "location": location
                },
                "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "fields": {
                    "value": value
                }
            }
    points.append(point)
    client.write_points(points)



logging.info("TempServer starting..")

# connexion a la base de données InfluxDB
# client = InfluxDBClient('192.168.1.17', 8086)
client = InfluxDBClient('influx', 8086)
db = "homedata"
connected = False
while not connected:
    try:
        logging.info("Check if database %s exists?", db)
        if not {'name': db} in client.get_list_database():
            logging.info("Database %s creation..", db)
            client.create_database(db)
            logging.info("Database %s created!", db)
        client.switch_database(db)
        logging.info("Connected to %s", db)
    except requests.exceptions.ConnectionError:
        logging.info('InfluxDB is not reachable. Waiting 5 seconds to retry.')
        time.sleep(5)
    else:
        connected = True




httpd.serve_forever()
