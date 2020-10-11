import numpy as np
from flask import Flask, request, jsonify, render_template
import joblib
from application.helpers import weather_for_model as weather
import pandas as pd
import json

app = Flask(__name__)
model = joblib.load('application/model')

def create_stations_json():
    df = pd.read_json("utils/stations.json")
    df = df[df['stationShortCodeCategory'] >= 0]
    df = df[['stationName',"stationShortCodeCategory"]].drop_duplicates()
    df.set_index('stationName',inplace=True)
    return df.to_dict()['stationShortCodeCategory']

stations = create_stations_json()

with open('utils/lines.json', 'r') as f:
    lines = json.load(f)

@app.route('/home')
def home():
    return render_template('index.html', stations=stations, lines=lines)

@app.route('/predict',methods=['POST'])
def predict():

    inputs = [int(x) for x in request.form.values()]
    select_station = request.form.get('station')
    select_station = int(select_station)
    select_line_str = request.form.get('lineID')
    select_line = int(select_line_str)

    print(inputs)
    weatherPrediction = weather.give_prediction(inputs[1], inputs[2], inputs[3], inputs[4])
    print(weatherPrediction)  # rain, celcius, windGustSpeed, windSpeed, station_name, weather_station, time_of_day
    inputs.extend(weatherPrediction[0:4])
    inputs = [select_line] + inputs[1:1] + [select_station] + inputs[2:]  
    features = [np.array(inputs)]
    print("feat ", features)

    direction = ', train coming from Helsinki main station' if inputs[5] == 1 else ', train going towards Helsinki main station'
    prediction_info = f'Date and time: {weatherPrediction[6].strftime("%d/%m/%Y %H:%M")}, train {lines.get(select_line_str)}, station {weatherPrediction[4]}{direction}'
    weather_info = f'Weather prediction for {weatherPrediction[5]} weather station: rain amount: {weatherPrediction[0]} mm/h, temperature: {weatherPrediction[1]} ℃, wind gusts: {weatherPrediction[2]} m/s, wind speed: {weatherPrediction[3]} m/s'
    features_sum = np.sum(features)

    if np.isnan(features_sum):
        return render_template('index.html', prediction_minutes='Cannot get a prediction for this time', stations=stations, lines=lines, prediction_info=prediction_info, weather_info=weather_info)

    prediction = model.predict(features)
    res = int(prediction[0])

    return render_template('index.html', prediction_minutes='Predicted train delay {} minute(s)'.format(res), stations=stations, lines=lines, prediction_info=prediction_info, weather_info=weather_info)

@app.route('/statistics', methods=['POST'])
def statistics():
    return render_template('statistics.html', stations=stations, lines=lines)
