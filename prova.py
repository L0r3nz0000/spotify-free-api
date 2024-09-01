import spotipy
from spotipy.oauth2 import SpotifyOAuth

auth_manager = SpotifyOAuth(
  client_id="92fc230dde1c46eeb6ff953580197100",
  client_secret="cca3aae793dc4922b01650d18d7b3b5b",
  redirect_uri="http://127.0.0.1:5000/callback",
  scope="user-read-playback-state")

sp = spotipy.Spotify(auth_manager)