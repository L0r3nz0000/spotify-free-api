from credentials import username, password
from login2 import login
import webbrowser
import requests
import base64
import json
import os

class App:
  def __init__(self, client_id, client_secret):
    if client_id:
      if client_secret:
        self.client_id = client_id
        self.client_secret = client_secret
      else:
        print('invalid client_secret')
    else:
      print('invalid client_id')

class SpotifyClient:
  s = requests.Session()
  
  def __init__(self, username, password):
    print("Sto ottenendo le credenziali per il player")
    self.player_access_token, self.client_id = login(username, password)
    
    if not self.player_access_token or not self.client_id:
      print("Login error")
      exit(1)

    self.player_headers = {
      'authorization': self.player_access_token
    }
    
    self.Bearer_token_1 = None
    self.devices = None
  
  def _send_command(self, command):
    to_id = self.get_playing_device(True)
    
    if self.devices:
      for device in self.devices['devices']:
        from_id = device['id']
        url = f'https://gew4-spclient.spotify.com/connect-state/v1/player/command/from/{from_id}/to/{to_id}'
        
        data = {
          "command": {
            "endpoint": command
          }
        }
        self.s.post(url, json=data, headers=self.player_headers)
    
  def pause(self):
    self._send_command('pause')
  
  def resume(self):
    self._send_command('resume')
    
  def next_track(self):
    self._send_command('skip_next')
  
  def prev_track(self):
    self._send_command('seek_to')
    
  def set_volume(self, value):
    to_id = self.get_playing_device(True)
    
    if self.devices:
      for device in self.devices['devices']:
        from_id = device['id']
        url = f'https://gew4-spclient.spotify.com/connect-state/v1/connect/volume/from/{from_id}/to/{to_id}'
        
        data = {
          'volume': round(value / 100.0 * 65535)
        }
        
        self.s.put(url, json=data, headers=self.player_headers)
        return True
    return False
  
  def _search(self, query: str, type: str):
    if self.Bearer_token_1:
      res = requests.get(f'https://api.spotify.com/v1/search?q={query}&type={type}&limit=10', headers={'Authorization': 'Bearer ' + self.Bearer_token_1}).json()
      return res
    else:
      print('app not authenticated')
  
  def search_track(self, query: str):
    return self._search(query, 'track')['tracks']['items'][0]
  
  def search_album(self, query: str):
    return self._search(query, 'album')['albums']['items'][0]
  
  def search_artist(self, query: str):
    return self._search(query, 'artist')['artists']['items'][0]
  
  def search_playlist(self, query: str):
    return self._search(query, 'playlist')['playlists']['items'][0]
  
  def play_something(self, uri):
    to_id = self.get_playing_device(True)
    
    if self.devices:
      for device in self.devices['devices']:
        from_id = device['id']
        
        url = f'https://gew4-spclient.spotify.com/connect-state/v1/player/command/from/{from_id}/to/{to_id}'
        json = {
          "command": {
            "context": {
              "url": f"context://{uri}"
            },
            "endpoint": "play"
          }
        }

        self.s.post(url, json=json, headers=self.player_headers)
  
  def _request_access_token(self, app: App):
    """Gets client credentials access token """
    url = 'https://accounts.spotify.com/api/token'
    
    payload = {"grant_type": "client_credentials"}
    
    encoded = base64.b64encode(f'{app.client_id}:{app.client_secret}'.encode()).decode()
    headers = {
      'content-type': 'application/x-www-form-urlencoded',
      'Authorization': 'Basic ' + encoded
    }

    print(f"sending POST request to {url} with Headers: {headers} and Body: {payload}")

    try:
      response = self.s.post(
        url,
        data=payload,
        headers=headers,
        verify=True
      )
      response.raise_for_status()
      token_info = response.json()
      return token_info
    except:
      return None
    
  def authorize_app(self, app: App, code, open_browser=False):
    if not os.path.exists('.cache') or open_browser:
      url = f'https://accounts.spotify.com/authorize?client_id={app.client_id}&scope=user-read-playback-state&response_type=code&redirect_uri=http://127.0.0.1:5000/callback'
      print('Opening url in browser\n')
      print(f'If not open, go to: {url}\n')
      webbrowser.get('firefox').open_new_tab(url)
      
      print('Aspetto il refresh token')
      # Aspetta che venga chiamata la callback a http://127.0.0.1:5000/callback
      while not code[0]: pass
    
      self.refresh_token = code[0]
    else:
      if os.path.exists('.cache'):
        with open('.cache', 'r') as file:
          print('Loading refresh token from .cache')
          data = file.read()
          if len(data):
            print('loading .cache')
            self.refresh_token = json.loads(data)['refresh_token']
          else:
            print('.cache empty')
            self.authorize_app(app, code, True)
    
    print(f'Refresh token: "{self.refresh_token}"')
    
    if self.refresh_token:
      token_info = self._request_access_token(app)
      
      if token_info:
        self.Bearer_token_1 = token_info['access_token']
        with open('.cache', 'w') as file:
          data = {
            'access_token': self.Bearer_token_1, 'token_type': 'Bearer',
            'refresh_token': self.refresh_token, 'scope': 'user-read-playback-state'
          }
          json.dump(data, file)
          print(".cache saved")
          
        print("Bearer devices token:", self.Bearer_token_1)
      else:
        print("Error: ", token_info)
        if token_info['error'] == 'invalid_grant':
          print('Trying with browser authentication')
          self.authorize_app(app, code, open_browser=True)
    else:
      print("No Basic token")
  
  def get_playing_device(self, update_devices=False):
    if self.devices and not update_devices:
      if self.devices:
        for device in self.devices['devices']:
          if device['is_active']:
            return device['id']
      return None
    else:
      if self.get_devices():
        return self.get_playing_device(False)
      else:
        print("Errore nell'otterimento dei dispositivi")
        return None
  
  def get_devices(self):
    if self.Bearer_token_1:
      headers = {
        'Authorization': 'Bearer ' + self.Bearer_token_1
      }
      
      self.devices = requests.get("https://api.spotify.com/v1/me/player/devices", headers=headers).json()
      return self.devices
    else:
      print("Errore nell'otterimento dei dispositivi")
      return None