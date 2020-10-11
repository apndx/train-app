#!/usr/bin/env python3

import os
import requests
from fmiopendata.wfs import download_stored_query
import datetime
import json
import pandas as pd
import json


def give_prediction(stationId, month, day, hour):
    place = "latlon=60.3267,24.95675" # default place is Veromiehenkylä
    stationShortCode = ''
    weather_area = 0
    station_name = ''
    with open("../utils/stations.json", 'r', encoding="utf-8") as f:
        stations = json.load(f)
        for station in stations:
            if station['stationShortCodeCategory'] == stationId:
                stationShortCode = station['stationShortCode']
                station_name = station['stationName']
                break
    if stationShortCode != '':
        with open("../utils/weather_stations.json", 'r', encoding="utf-8") as f:
            weather_stations = json.load(f)
            weather_area = weather_stations.get(stationShortCode)
        with open("../utils/weather-locations.json", 'r', encoding="utf-8") as f:
            places = json.load(f)
            place = places.get(str(weather_area))['latlon']

    now = datetime.datetime.utcnow()
    end_time = datetime.datetime(now.year, month, day, hour)
    start_time = end_time - datetime.timedelta(hours=1)
    # Convert times to properly formatted strings
    start_time = start_time.isoformat(timespec="seconds") + "Z"
    # -> 2020-07-07T12:00:00Z
    end_time = end_time.isoformat(timespec="seconds") + "Z"
    # -> 2020-07-07T13:00:00Z
    obs = download_stored_query("fmi::forecast::hirlam::surface::point::multipointcoverage",
                                args=["starttime=" + start_time, "endtime=" + end_time, place])

    print(obs.location_metadata)
    print(obs.data)
    time_of_day = max(obs.data.keys())
    print('timestamp', time_of_day)

    weather_station = list(obs.data[time_of_day].keys())[0]
    print(weather_station)

    data = obs.data[time_of_day][weather_station]
    rain = data['Precipitation amount 1 hour']['value']
    celcius = data['Air temperature']['value']
    windGustSpeed = data['Wind gust']['value']
    windSpeed = data['Wind speed']['value']

    weather = [rain, celcius, windGustSpeed, windSpeed, station_name, weather_station, time_of_day]
    return weather
