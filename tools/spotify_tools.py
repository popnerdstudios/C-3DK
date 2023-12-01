import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
scope = 'user-modify-playback-state'

def play_song(song_name):
    spotify_search = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = spotify_search.search(q=song_name, limit=1, type='track')
    tracks = results['tracks']['items']
    
    if not tracks:
        print("No tracks found.")
        return

    track_uri = tracks[0]['uri']
    print(track_uri)

    spotify_playback = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                                client_secret=client_secret,
                                                                redirect_uri=redirect_uri,
                                                                scope='user-modify-playback-state'))

    try:
        spotify_playback.start_playback(uris=[track_uri])
        print(f"Playing: {tracks[0]['name']} by {', '.join(artist['name'] for artist in tracks[0]['artists'])}")
    except spotipy.SpotifyException as e:
        print(f"Error starting playback: {e}")

def play_album(album_name):
    spotify_search = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = spotify_search.search(q=album_name, limit=1, type='album')
    albums = results['albums']['items']
    
    if not albums:
        print("No albums found.")
        return

    album_uri = albums[0]['uri']
    print(album_uri)

    spotify_playback = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                                client_secret=client_secret,
                                                                redirect_uri=redirect_uri,
                                                                scope='user-modify-playback-state'))

    try:
        spotify_playback.start_playback(context_uri=album_uri)
        print(f"Playing album: {albums[0]['name']} by {', '.join(artist['name'] for artist in albums[0]['artists'])}")
    except spotipy.SpotifyException as e:
        print(f"Error starting playback: {e}")

def get_user_playlists(_=None):
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                        client_secret=client_secret,
                                                        redirect_uri=redirect_uri,
                                                        scope='playlist-read-private'))

    try:
        results = spotify.current_user_playlists(limit=50)
        playlists = results['items']
        while results['next']:
            results = spotify.next(results)
            playlists.extend(results['items'])
        return [(playlist['name'], playlist['uri']) for playlist in playlists]
    except spotipy.SpotifyException as e:
        print(f"Error fetching playlists: {e}")
        return []
    

def play_spotify_uri(uri):
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                        client_secret=client_secret,
                                                        redirect_uri=redirect_uri,
                                                        scope='user-modify-playback-state'))

    try:
        if "track" in uri:
            spotify.start_playback(device_id=None, uris=[uri])
        else:
            spotify.start_playback(device_id=None, context_uri=uri)
        print("Playback started.")
    except spotipy.SpotifyException as e:
        print(f"Error starting playback: {e}")

def spotify_controller(command):
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                        client_secret=client_secret,
                                                        redirect_uri=redirect_uri,
                                                        scope=scope))
    try:
        if command == "start":
            spotify.start_playback()
        elif command == "pause":
            spotify.pause_playback()
        elif command == "next" or command == "skip":
            spotify.next_track()
        elif command == "previous":
            spotify.previous_track()
        elif command == "shuffle":
            current_playback = spotify.current_playback()
            if current_playback and current_playback['shuffle_state']:
                spotify.shuffle(False)
            else:
                spotify.shuffle(True)
        else:
            print(f"Unknown command: {command}")
    except spotipy.SpotifyException as e:
        print(f"Error controlling playback: {e}")