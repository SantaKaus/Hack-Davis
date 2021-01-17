from flask import Flask, render_template, url_for
from pyowm import OWM
from flask import jsonify

from flask_cors import CORS
from sklearn import tree
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import CountVectorizer
import http.client
import json
import pandas as pd
import requests


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

@app.route('/movies') #split function in 2 pieces, one to split and json the other part to time loop/background jobs 
def movies():
    OMDBAPIKey = "778e5667"
    APIKey = "e20e035943ec00333eb2a1d09ea93a5c"
    NewsAPIKey = "e585b7de092d4ccbbe055c71425b5dca"

    news_training_texts = []
    tmdb_testing_texts = []
    tmdb_testing_texts_ids = []

    final_list = []
# the range is the number of pages we are going through
    for y in range(1, 2):
        tmdbhttpRequest = "https://api.themoviedb.org/3/movie/popular?api_key=e20e035943ec00333eb2a1d09ea93a5c&language=en-US&page=" + str(
          y)
        tmdbresponse = requests.get(tmdbhttpRequest)
        tmdbdata = tmdbresponse.json()
        text = json.dumps(tmdbdata, sort_keys=True, indent=4)
        #print(text)
        for z in tmdbdata["results"]:
            tmdbtexts = z["title"] + " " + z["overview"] + " "
            movieArray = [z["title"]]
            if ("release_date" in z):
                movieArray.append(z["release_date"])
            else:
                movieArray.append("")
            movieArray.append(z["overview"])
            movieArray.append(z["poster_path"])
            tmdb_testing_texts_ids.append(movieArray)
            # tmdb_testing_texts_ids.append([z["title"], z["release_date"], z["overview"], z["poster_path"]])
            keywords = requests.get(
              "https://api.themoviedb.org/3/movie/" + str(z["id"]) +
              "/keywords?api_key=e20e035943ec00333eb2a1d09ea93a5c").json()
            for x in keywords["keywords"]:
                tmdbtexts = tmdbtexts + x["name"] + " "
            tmdb_testing_texts.append(tmdbtexts)

    for y in range(1, 2):
        tmdbhttpRequest = "https://api.themoviedb.org/3/tv/popular?api_key=e20e035943ec00333eb2a1d09ea93a5c&language=en-US&page=" + str(
          y)
        tmdbresponse = requests.get(tmdbhttpRequest)
        tmdbdata = tmdbresponse.json()
        for z in tmdbdata["results"]:
            tmdb_testing_texts_ids.append(
              [z["name"], z["first_air_date"], z["overview"], z["poster_path"]])
            tmdbtexts = z["name"] + " " + z["overview"] + " "
            keywords = requests.get(
              "https://api.themoviedb.org/3/tv/" + str(z["id"]) +
              "/keywords?api_key=e20e035943ec00333eb2a1d09ea93a5c").json()
            for x in keywords["results"]:
                tmdbtexts = tmdbtexts + x["name"] + " "
            tmdb_testing_texts.append(tmdbtexts)

    #https://medium.com/towards-artificial-intelligence/similar-texts-search-in-python-with-a-few-lines-of-code-an-nlp-project-9ace2861d261
    newshttpRequest = "https://newsapi.org/v2/top-headlines?country=us&apiKey=" + NewsAPIKey
    newsresponse = requests.get(newshttpRequest)
    newsdata = newsresponse.json()
    for x in newsdata["articles"]:
        if isinstance(x["description"], str):
            newstext = x["title"] + x["description"]
        else:
            newstext = x["title"]
        tmdb_testing_texts.append(newstext)
        vect = CountVectorizer()
        word_weight = vect.fit_transform(tmdb_testing_texts)
        nm = NearestNeighbors(metric='euclidean')
        nm.fit(word_weight)
        distances, indices = nm.kneighbors(
           word_weight[word_weight.shape[0] - 1], n_neighbors=4)
        neighbors = pd.DataFrame({
           'distance': distances.flatten(),
           'id': indices.flatten()
        })
        one = tmdb_testing_texts_ids[indices.flatten()[1]]
        two = tmdb_testing_texts_ids[indices.flatten()[2]]
        three = tmdb_testing_texts_ids[indices.flatten()[3]]
        final_list.append([x["title"], [one, two, three]])
        tmdb_testing_texts.pop()

    count = 0
    for i in final_list:
        print("News Article #", count)
        count += 1
        n = 0
        for j in i:
            print(j)
            n += 1
    print("end")

    return jsonify(final_list)
# movieArray = movies()

if __name__ == "__main__":
    app.run(debug=True)

    