import pickle
import streamlit as st
import requests
import pandas as pd
import difflib

# Replace with your actual OMDb API key
OMDB_API_KEY = '8c9a2313'

def get_poster_url(movie_title):
    """Fetch the poster URL for a given movie title from OMDb."""
    # Attempt to get the poster using the exact title
    search_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={movie_title}"
    response = requests.get(search_url)
    data = response.json()

    if data['Response'] == 'True':
        poster_url = data['Poster']
        if poster_url != 'N/A':
            return poster_url
    else:
        # If no exact match, search for the closest match
        search_results = requests.get(f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={movie_title}").json()
        if search_results['Response'] == 'True':
            # Find the best match based on title similarity
            best_match = max(search_results['Search'], key=lambda x: difflib.SequenceMatcher(None, x['Title'], movie_title).ratio())
            # Get the poster for the best match
            search_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={best_match['Title']}"
            response = requests.get(search_url)
            data = response.json()
            poster_url = data['Poster']
            if poster_url != 'N/A':
                return poster_url
    return None  # Return None if no poster found

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []

    for i in movies_list:
        movie_id = i[0]
        title = movies.iloc[i[0]]['title']
        poster_url = get_poster_url(title)  # Fetch the poster URL
        recommended_movies.append({
            'title': title,
            'poster_url': poster_url  # Use the fetched poster URL
        })

    return recommended_movies

# Load movies and similarity data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit app starts here
st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie from the dropdown:',
    movies['title'].values
)

if st.button('Recommended'):
    recommendations = recommend(selected_movie_name)
    for movie in recommendations:
        st.write(movie['title'])  # Display movie title
        if movie['poster_url']:
            st.image(movie['poster_url'], width=200)  # Display movie poster
        else:
            st.write("Poster not available")  # Handle cases where no poster is found

