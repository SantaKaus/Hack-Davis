from flask import Flask, render_template, url_for
from pyowm import OWM
from flask_cors import CORS

app=Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

owm = OWM('3934d6152a96aacb472b934be3eda2ff')
@app.route('/weather/<city>')
def weather(city):
    print(city)
    obs = owm.weather_at_place(f'{city},US')
    w = obs.get_weather() 
    return w.get_temperature()

    #return weather_at_place.weather.temperature('celsius')
    #return weather_at_place.get_reception_time()      


if __name__ == "__main__":
    app.run(debug=True)

    