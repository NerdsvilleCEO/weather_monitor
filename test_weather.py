#!/bin/python
from dotenv import load_dotenv
import logging
import os
import requests

load_dotenv()
logging.basicConfig(filename="weather_alerts.log", 
                    level=logging.INFO, 
                    datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)s %(message)s')

def convert_celsius_to_farenheit(celsius):
    return celsius * 1.8 + 32

"""
  Class to generate a weather flow device/station tester object

  Notes:
    Currently only works for one station/device combination, could be 
  refactored to support many.

    Only runs once, grabs the values, compares and logs to file,
  this is something which can be later improved to poll over a certain interval
  or to use WebSockets.

    Does not support entire API, only tests temperature and precipitation.
"""
class WeatherFlowTester:
    def get_test_station_url(self):
        return "https://swd.weatherflow.com/swd/rest/observations/station/{}?api_key={}".format(os.getenv("STATION_ID"), os.getenv("API_KEY"))

    def alert(self, alertType, deviation):
        if alertType == "prec":
            logging.info("Weather exceeded threshold for Percipitation by: {}%".format(deviation))
        elif alertType == "air_temperature":
            logging.info("Weather exceeded threshold for Temperature by: {} degrees".format(deviation))
        
    def test_precipitation(self, data):
        prec_operator = os.getenv("PREC_OPERATOR")
        if prec_operator == "gt":
            if data['obs'][0]['precip'] > os.getenv("PREC_THRESHOLD"):
                self.alert("precip", data[0]['precip'])
        elif prec_operator == "lt":
            if data['obs'][0]['precip'] < os.getenv("PREC_THRESHOLD"):
                self.alert("precip", data[0]['precip'])

    def test_temperature(self, data):
        temp_operator = os.getenv("TEMP_OPERATOR")
        temp_threshold = float(os.getenv("TEMP_THRESHOLD"))
        air_temp = convert_celsius_to_farenheit(data['obs'][0]['air_temperature'])
        if temp_operator == "gt":
            if air_temp > temp_threshold:
                self.alert("air_temperature", air_temp - temp_threshold)
        elif temp_operator == "lt":
            if air_temp < temp_threshold:
                self.alert("air_temperature", temp_threshold - air_temp)

    def test_weather(self):
        r = requests.get(self.get_test_station_url())
        data = r.json()
        self.test_precipitation(data)
        self.test_temperature(data)

tester = WeatherFlowTester()
tester.test_weather()
