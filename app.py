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


# returnList = [
# ["Hot pockets recalled for possible glass, plastic contamination | TheHill - The Hill",
# [['Vanguard', '2020-09-30', "Covert security company Vanguard is the last hope of survival for an accountant after he is targeted by the world's deadliest mercenary organization.", '/vYvppZMvXYheYTWVd8Rnn9nsmNp.jpg'], ["Dory's Reef Cam", '2020-12-18', 'Dive into the waters below and watch the aquatic wildlife from the world of Nemo and Dory.', '/mMWLGu9pFymqipN8yvISHsAaj72.jpg'], ['Lupin', '2021-01-08', 'Inspired by the adventures of Arsène Lupin, gentleman thief Assane Diop sets out to avenge his father for an injustice inflicted by a wealthy family.', '/sgxawbFB5Vi5OkPWQLNfl3dvkNJ.jpg']]],
# ["Nets 122, Magic 115: James Harden Posts Triple-Double in Brooklyn Debut | Brooklyn Nets - Brooklynnets.com",
# [["Dory's Reef Cam", '2020-12-18', 'Dive into the waters below and watch the aquatic wildlife from the world of Nemo and Dory.', '/mMWLGu9pFymqipN8yvISHsAaj72.jpg'], ['Vanguard', '2020-09-30', "Covert security company Vanguard is the last hope of survival for an accountant after he is targeted by the world's deadliest mercenary organization.", '/vYvppZMvXYheYTWVd8Rnn9nsmNp.jpg'], ['Equinox', '2020-12-30', 'Haunted by visions after her sister vanished with her classmates 21 years before, Astrid begins an investigation that uncovers the dark, eerie truth.', '/bnU3Rz3nR844WZNOyrCk8W52DUs.jpg']]],
# ["Ga. lawyer, mother of ‘zip-tie guy’ charged in Capitol riot - Atlanta Journal Constitution",
# [['Vanguard', '2020-09-30', "Covert security company Vanguard is the last hope of survival for an accountant after he is targeted by the world's deadliest mercenary organization.", '/vYvppZMvXYheYTWVd8Rnn9nsmNp.jpg'], ['Lupin', '2021-01-08', 'Inspired by the adventures of Arsène Lupin, gentleman thief Assane Diop sets out to avenge his father for an injustice inflicted by a wealthy family.', '/sgxawbFB5Vi5OkPWQLNfl3dvkNJ.jpg'], ["Dory's Reef Cam", '2020-12-18', 'Dive into the waters below and watch the aquatic wildlife from the world of Nemo and Dory.', '/mMWLGu9pFymqipN8yvISHsAaj72.jpg']]]
# ]
# def algorithm():

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
    print("length of final list ", len(final_list[0]))
    # returnList = final_list
    return jsonify(final_list)

    #count = 0 debug
    # for i in final_list:
    #     print("News Article #", count)
    #     count += 1
    #     n = 0
    #     for j in i:
    #         print(j)
    #         n += 1
    # print("end")
    # return jsonify(final_list)
# algorithm()

# @app.route('/movies') #split function in 2 pieces, one to split and json the other part to time loop/background jobs 
# def movies():
    # return jsonify(returnList)

if __name__ == "__main__":
    app.run(debug=True)

    