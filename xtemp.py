from urllib.request import urlopen
import json
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server
import requests
import datetime
import time
from lywsd03mmc import Lywsd03mmcClient
from datetime import datetime
import errno
import logging

logging.basicConfig(level=logging.DEBUG,filename='/tmp/xiaomiapp.log', filemode='a', format='%(asctime)s: %(levelname)s - %(message)s')
logging.debug("Let's start")

def connect(address):
    try:
      client = Lywsd03mmcClient(address)
      logging.debug("Try to fetch from: " + address)
      return client
    except socket.error as e:
      if e.errno == errno.EPIPE:
        logging.debug("Error catch data, brocken pipe")

class CustomCollector(object):
    def __init__(self):
        pass

    def collect(self):

      try:
        client1 = connect("A4:C1:38:19:2D:04")
        client2 = connect("A4:C1:38:FF:24:D1")
        client3 = connect("A4:C1:38:14:F9:AD")
      except:
        logging.debug("Error connection to sensor")
        pass

      try:
        client1 = Lywsd03mmcClient("A4:C1:38:19:2D:04")
        client2 = Lywsd03mmcClient("A4:C1:38:FF:24:D1")
        client3 = Lywsd03mmcClient("A4:C1:38:14:F9:AD")
      except socket.error as e:
        if e.errno == errno.EPIPE:
          logging.debug("Error catch data, brocken pipe")
        pass

      temp_child = 0
      temp_parents = 0
      temp_balcony = 0
      hum_child = 0
      hum_parents = 0
      hum_balcony = 0
      bat_child = 0
      bat_parents = 0
      bat_balcony = 0

      dateTimeObj = datetime.now()
      timestampStr = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S")


      try:
        data_child = client1.data
        data_parent = client2.data
        data_balcony = client3.data
      except:
        logging.debug("Error reading data")
        pass

      try:
        temp_child = data_child.temperature
        temp_parents = data_parent.temperature
        temp_balcony = data_balcony.temperature
        hum_child = data_child.humidity
        hum_parents = data_parent.humidity
        hum_balcony = data_balcony.humidity
        bat_child = data_child.battery
        bat_parents = data_parent.battery
        bat_balcony = data_balcony.battery
      except:
        logging.debug("Error catch data")
        pass

      g = GaugeMetricFamily("temperature", 'Temperature from xiaomi termo', labels=['location'])
      g.add_metric(["children"],temp_child)
      g.add_metric(["parents"],temp_parents)
      g.add_metric(["balcony"],temp_balcony)
      yield g

      h = GaugeMetricFamily("humidity", 'Humidity from xiaomi termo', labels=['location'])
      h.add_metric(["children"],hum_child)
      h.add_metric(["parents"],hum_parents)
      h.add_metric(["balcony"],hum_balcony)
      yield h

      b = GaugeMetricFamily("battery", 'Battery from xiaomi termo', labels=['location'])
      b.add_metric(["children"],bat_child)
      b.add_metric(["parents"],bat_parents)
      b.add_metric(["balcony"],bat_balcony)
      yield b

if __name__ == '__main__':
    start_http_server(8001)
    REGISTRY.register(CustomCollector())
    while True:
      time.sleep(25)
