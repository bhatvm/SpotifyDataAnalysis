import spotipy
from spotipy import SpotifyClientCredentials
import json
import pandas as pd
from pandas.io.json import json_normalize

def spotify_search_as_df(spotify_object,keyword = "",type = "playlist"):
    playlists = spotify_object.search(q=keyword,type = type)
    print("Searching for all " + type + " with keyword : " + keyword + " ..... ")
    playlist_search = json_normalize(playlists[type+"s"]["items"])
    return playlist_search

def get_playlist_songs_metadata(spotify_object,playlist_name = " ",playlist_id = " ",owner = " "):
    #print(owner)
    playlist = spotify_object.user_playlist(user=owner,playlist_id=playlist_id)
    tracks_metadata = json_normalize(playlist["tracks"]["items"])
    return tracks_metadata

def get_songfeatures_(spotify_object,track_id = " "):
    #print(track_id)
    songs_features = json_normalize(spotify_object.audio_features(track_id))
    return songs_features

# def __main__():
#     if __name__ == "__main__":
        
# Get Credentials
with open("credentials.json") as f:
    cred = json.load(f)

CLIENT_ID = cred["Client_ID"] #from developers.spotify.com
CLIENT_SECRET = cred["Client_Secret"] #from developers.spotify.com

# Login to the API
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Get the top tracks playslists over the years    
keywords = "Top Tracks of "
years = (2016,2017,2018,2019,2020) 
owner = "Spotify"

for i,year in enumerate(years):
    keyword = keywords+str(year)
    print(keyword)
    if(i==0):
        playlist_search = spotify_search_as_df(sp,keyword=keyword)
        playlist_search_master = playlist_search[(playlist_search["name"]==keyword) & (playlist_search["owner.display_name"]==owner)]
    else:
        playlist_search = playlist_search.append(spotify_search_as_df(sp,keyword=keyword),ignore_index = True)
        playlist_search = playlist_search[(playlist_search["name"]==keyword) & (playlist_search["owner.display_name"]==owner)]
        playlist_search_master = playlist_search_master.append(playlist_search,ignore_index = True)        

# Get the tracks from playlist master and their audio features

for i in range(0,len(playlist_search_master)):
    playlist = playlist_search_master.loc[i]
    tracks_metadata = get_playlist_songs_metadata(sp,playlist_name=playlist["name"],playlist_id=playlist["id"],
    owner=playlist["owner.display_name"])
    song_master = pd.DataFrame()

    for j in range(0,len(tracks_metadata)):
        
        song = pd.DataFrame()
        
        song = get_songfeatures_(sp,track_id=tracks_metadata["track.id"].loc[j])
        song["name"] = tracks_metadata["track.name"].loc[j]
        song["id"] = tracks_metadata["track.id"].loc[j]
        song["album"] = tracks_metadata["track.album.name"].loc[j]
        song["artist"] = ' , '.join(json_normalize(tracks_metadata["track.artists"].loc[j])["name"])
        song["duration_ms"] = tracks_metadata["track.duration_ms"].loc[j]
        song["track.popularity"] = tracks_metadata["track.popularity"].loc[j]
        song["track.album.release_date"] = tracks_metadata["track.album.release_date"].loc[j]

        if(j==0):
            song_master = song
        else:
            song_master = song_master.append(song,ignore_index = True)
    
    song_master["playlist_name"] = playlist["name"]
    if(i==0):
        song_features_master = song_master
    else:
        song_features_master = song_features_master.append(song_master,ignore_index = True)
    
song_features_master.to_csv("data/Top tracks by Spotify - 2016-2019.csv")