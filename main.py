from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# load the environment variables
load_dotenv()

# create a spotify object using the spotipy library and the SpotifyOAuth class to authenticate the user and
# get the token from the user and store it in the token.txt file
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv("CLIENT_ID"),
                                               client_secret=os.getenv("CLIENT_SECRET"),
                                               redirect_uri=os.getenv("REDIRECT_URI"),
                                               scope="playlist-modify-private",
                                               show_dialog=True,
                                               cache_path="token.txt"))

# get the user id from the spotify api and store it in the user_id variable
user_id = sp.current_user()["id"]

# Get the date from the user
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

# Use the date to get the top 100 songs from that date
response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}")

# Use BeautifulSoup to parse the html file
billboard_web_page = response.text

# gets BeautifulSoup object from the html file and parses it using the html.parser to help beautiful soup understand
soup = BeautifulSoup(billboard_web_page, "html.parser")

# get all the tags that start with the li tag that has the song title in it and eventually getting the h3 tag
# with the song title
song_tags = soup.select("li ul li h3")

# get the text inside the h3 tag and strip it of any whitespace and append it to the songs list
songs = [song.getText().strip() for song in song_tags]

# create a list of spotify uris for the songs
song_uris = []
# date.split("-")[0] gets the year from the date variable by splitting the date at the "-" into 3 parts and getting
# the first part which is the year hence the [0]
year = date.split("-")[0]
# search for the song in spotify and get the uri for the song and append it to the song_uris list if the song exists
# in spotify
for song in songs:
    result = sp.search(q=f"track:{song} year:{year}", limit=1, type="track", market="US")
    # try and except block to catch the IndexError if the song doesn't exist in spotify and print a message to the user
    try:
        # track uri is the uri for the song and items[0] is the first item in the list of items returned by the search
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# create a new private playlist in spotify and get the playlist id
# to create a private playlist we need to set the public parameter to False, get user_id to create the playlist
# for the specific user and get the date from the user to name the playlist accordingly
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)

# get the playlist id from the playlist object returned by the user_playlist_create method
playlist_id = playlist["id"]
# add the songs to the playlist if the song_uris list is not empty and the playlist_id is not None or empty string
for song in song_uris:
    # add the songs to the playlist using the playlist_add_items method and passing in the playlist_id and
    # the song_uris list as the items parameter to add the songs to the playlist in spotify
    sp.playlist_add_items(playlist_id=playlist_id, items=song_uris, position=None)



