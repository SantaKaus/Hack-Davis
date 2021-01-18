from sklearn import tree
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import CountVectorizer
import http.client
import json
import pandas as pd
import numpy as np
import requests
import pickle
from random import randint
import random

# something im trying
from sklearn.feature_extraction.text import TfidfVectorizer

OMDBAPIKey = "778e5667"
APIKey = "e20e035943ec00333eb2a1d09ea93a5c"
NewsAPIKey = "e585b7de092d4ccbbe055c71425b5dca"

""""
news_training_texts = []
petitions_testings_texts = []
tmdb_testing_texts = []
tmdb_testing_texts_ids = []
"""

#text_master = []

petition_file = open('/var/www/html/petitions500.json')
petition_data = json.load(petition_file)

petition_string_list = []
petition_string_list_ids = []

for petition in petition_data["petitions"]:
  petition_string = petition["title"] + " " + petition["description"]
  petition_string_list.append(petition_string)
  petition_string_list_ids.append([petition["title"], petition["url"], petition["image_url"]]) 

news_string_list = []

newshttpRequest = "https://newsapi.org/v2/top-headlines?country=us&apiKey="+NewsAPIKey
newsresponse = requests.get(newshttpRequest)
newsdata = newsresponse.json()
for x in newsdata["articles"]:
  if isinstance(x["description"], str):
    newstext = x["title"] + " ## " + x["description"] 
  else: 
    # if no description forget about this article
    continue

  news_string_list.append(newstext)

final_list = []

# find most similar news article to petition or vice versa?
# news article most similar to petition:
for petition in petition_data["petitions"]:
  petition_string = petition["title"] + " " + petition["description"]

  vect = TfidfVectorizer(min_df=1, stop_words="english")
  temp_list = [petition_string] + news_string_list
  tfidf = vect.fit_transform(temp_list)
  pairwise_similarity = tfidf * tfidf.T

  # now we have pairwise_similarity matrix with index 0 being the petition in question, we want to find the news article (from every other index) most similar to petition
  # to do this we take the argmax of row 0, but mask the 1's as nan

  arr = pairwise_similarity.toarray()
  np.fill_diagonal(arr, np.nan)

  input_text = petition_string
  input_index = temp_list.index(input_text)
  result_index = np.nanargmax(arr[input_index])

  news_text = temp_list[result_index]
  news_title = news_text[:news_text.index(" ## ")]

  final_list.append([news_title, [petition["title"], petition["url"], petition["image_url"]]])

random.shuffle(final_list)

with open("/var/www/html/final_list.pickle", "wb") as f:
    pickle.dump(final_list, f)
