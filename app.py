from flask import Flask, request, render_template, send_file, jsonify
import json
import os
import requests
import requests
import json
import wget
from datetime import datetime



def get_weather(loc: list = []):
    datas = {}

    wget.download(f"https://api.open-meteo.com/v1/forecast?latitude={loc[0]}&longitude={loc[1]}&current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,rain,snowfall,surface_pressure,wind_speed_10m,wind_direction_10m,is_day&forecast_days=1", "weather.json")
    
    with open("weather.json", "r", encoding="utf-8") as f:
        weather = json.loads(f.read())
        f.close()
    
    os.remove("weather.json")

    datas = {
        "current": {
            "temperature": weather["current"]["temperature_2m"],
            "humidity": weather["current"]["relative_humidity_2m"],
            "rain":  weather["current"]["rain"],
            "wind_speed":  weather["current"]["wind_speed_10m"],
        },
        "hourly":  {}
    }

    for element in range(0,24):
        datas["hourly"][f"{element}:00"] = {
            "temperature": weather["hourly"]["temperature_2m"][element],
            "humidity": weather["hourly"]["relative_humidity_2m"][element],
            "precipitation": weather["hourly"]["precipitation_probability"][element],
            "rain": weather["hourly"]["rain"][element],
            "snowfall": weather["hourly"]["snowfall"][element],
            "surface_pressure": weather["hourly"]["surface_pressure"][element],
            "is_day": weather["hourly"]["is_day"][element],
        }

    return datas

path = os.getcwd()+"/apps/Weather"
app = Flask(__name__)

@app.route('/')
def page_home():
    with open(f"{path}/index.html", "r", encoding="utf-8") as f:
        page = f.read()
        f.close()


    with requests.get("https://ipinfo.io/json") as r:
        loc = json.loads(r.text)["loc"].split(",")
        city = json.loads(r.text)["city"]
        r.close()
    
    weather = get_weather(loc)

    page = page.replace("$city", city)
    page = page.replace("$date", str(datetime.now().strftime("%d/%m/%Y")))

    page = page.replace("$current_temp", str(weather["current"]["temperature"]))
    page = page.replace("$current_humidty", str(weather["current"]["humidity"]))
    page = page.replace("$current_rain", str(weather["current"]["rain"]))
    page = page.replace("$current_wind_speed", str(weather["current"]["wind_speed"]))


    hourly_weather_total = ""
    for hourly_weather in range(0,24):
        hourly_weather_total += f"""
<li class="list-group-item">
    <details>
    <summary><ion-icon name="{str(weather['hourly'][f'{hourly_weather}:00']['is_day']).replace('0','moon').replace('1','sunny')}"></ion-icon> Prévisions pour {hourly_weather}:00 </summary>
    <p>
        <ion-icon name="thermometer"></ion-icon> Température : {weather['hourly'][f'{hourly_weather}:00']['temperature']} °C<br>
        <ion-icon name="water"></ion-icon> Humidité : {weather['hourly'][f'{hourly_weather}:00']['humidity']} %<br>
        <ion-icon name="dice"></ion-icon> Probabilité de précipitation (pluie) : {weather['hourly'][f'{hourly_weather}:00']['precipitation']} %<br>
        <ion-icon name="rainy"></ion-icon> Pluie : {weather['hourly'][f'{hourly_weather}:00']['rain']} mm<br>
        <ion-icon name="snow"></ion-icon> Neige : {weather['hourly'][f'{hourly_weather}:00']['snowfall']} mm<br>
        <ion-icon name="stopwatch"></ion-icon> Pression atmosphérique : {weather['hourly'][f'{hourly_weather}:00']['surface_pressure']} hPa<br>
    </p>
    </details>
</li>
"""

    page = page.replace("$hourly_weather_total", hourly_weather_total)
    del hourly_weather_total
    return page

# Fichiers
@app.route('/css')
def css():
    return send_file(f"{path}/style.css")

@app.route('/images/logo.png')
def logo():
    return send_file(f"{path}/images/logo.png")
    
@app.route('/images/background.png')
def background():
    return send_file(f"{path}/images/background.png")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5501)