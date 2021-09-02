from flask import Flask,render_template,request
import urllib
import urllib.request as requestURL
import json
import requests
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity 

app = Flask(__name__)
dataset = pd.read_csv('final_movie_data.csv')


def get_title_from_index(index):
    return dataset[dataset.index == index]['movie_title'].values[0]
def get_index_from_title(title):
    return dataset[dataset.movie_title== title].index.values[0]

def get_imdb_from_title(title):
    return dataset[dataset.movie_title== title]['imdb_id'].values[0]

def get_id_from_index(index):
    return dataset[dataset.index == index]['id'].values[0]

def get_imdb_from_index(index):
    return dataset[dataset.index == index]['imdb_id'].values[0]
def get_id_from_title(title):
    return dataset[dataset.movie_title== title]['id'].values[0]


def suggestion(id):
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(dataset['combine'])
    similarty_scores = cosine_similarity(count_matrix)
    #movie_index =get_index_from_title(movie_name)
    movie_index= int(id)
    similar_movies = list(enumerate(similarty_scores[movie_index]))
    sorted_movies = sorted(similar_movies,key= lambda x:x[1],reverse=True)
    recommed_movies_index = sorted_movies[1:6]
    recommended_movies =[]
    for movie in recommed_movies_index:
        recommended_movies.append(get_id_from_index(movie[0]))
    movie_list=[]
    for i in range(0,5):
        movie_url = 'https://api.themoviedb.org/3/find/'+recommended_movies[i]+'?api_key=529773cc0b21e996d3e064017be3fd99&external_source=imdb_id'
        conn5 = requestURL.urlopen(movie_url)
        recommended_movie_data = json.loads(conn5.read())
        movie_list.append(recommended_movie_data['movie_results'])
        recommended_movie_list = np.array(movie_list)
        recommended_movie_dict = recommended_movie_list.flatten()
    return  recommended_movie_dict
                  

@app.route('/',methods=['GET'])
def index():
    popular_url = 'https://api.themoviedb.org/3/movie/popular?api_key=529773cc0b21e996d3e064017be3fd99'
    conn = requestURL.urlopen(popular_url)
    popular_movie_data = json.loads(conn.read())
    select_movie_data = popular_movie_data['results']
    
    
    latest_url ='https://api.themoviedb.org/3/movie/top_rated?api_key=529773cc0b21e996d3e064017be3fd99&language=en-US'
    conn_latest = requestURL.urlopen(latest_url)
    latest_movie_dict = json.loads(conn_latest.read())
    latest_movie_data = latest_movie_dict['results']
    
   
    return  render_template('index.html',select_movie_data=select_movie_data,latest_movie_data=latest_movie_data)
 
    
@app.route('/reommened',methods=['GET','POST']) 
def recommend():
     if request.method == 'POST':
          movie_name = (request.form['q'])
          query = str(get_id_from_title(movie_name))
          
          if query:
               base_url = 'https://api.themoviedb.org/3/movie/'+query+'?api_key=529773cc0b21e996d3e064017be3fd99&external_source=imdb_id'
               conn = requestURL.urlopen(base_url)
               movie_data = json.loads(conn.read())
               cast_url = 'https://api.themoviedb.org/3/movie/'+query+'/credits?api_key=529773cc0b21e996d3e064017be3fd99'
               conn1 = requestURL.urlopen(cast_url)
               cast_data = json.loads(conn1.read())
               cast_dict = cast_data['cast'][:6]
               #get reviews
               
               #review_url = 'https://api.themoviedb.org/3/movie/'+query+'/reviews?api_key=529773cc0b21e996d3e064017be3fd99&language=en-US&page=1'
               #conn3 = requestURL.urlopen( review_url)
               #review_data = json.loads(conn3.read())
               #review_data = review_data['results']
               #recommendation
               cv = CountVectorizer()
               count_matrix = cv.fit_transform(dataset['combine'])
               similarty_scores = cosine_similarity(count_matrix)
               movie_index =get_index_from_title(movie_name)
               similar_movies = list(enumerate(similarty_scores[movie_index]))
               sorted_movies = sorted(similar_movies,key= lambda x:x[1],reverse=True)
               recommed_movies_index = sorted_movies[1:10]
               recommended_movies =[]
               for movie in recommed_movies_index:
                   recommended_movies.append(get_imdb_from_index(movie[0]))
               movie_list=[]
               for i in range(0,9):
                  movie_url = 'https://api.themoviedb.org/3/find/'+recommended_movies[i]+'?api_key=529773cc0b21e996d3e064017be3fd99&external_source=imdb_id'
                  conn5 = requestURL.urlopen(movie_url)
                  recommended_movie_data = json.loads(conn5.read())
                  movie_list.append(recommended_movie_data['movie_results'])
                  recommended_movie_list = np.array(movie_list)
                  recommended_movie_dict = recommended_movie_list.flatten()
    
               
               return  render_template('movie.html',movie_data=movie_data,cast_dict=cast_dict,recommended_movie_dict=recommended_movie_dict,)
           
     return  render_template('movie.html')
    
    
if __name__=="__main__":
    app.run(debug=True)