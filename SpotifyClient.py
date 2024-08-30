from credentials import username, password
from login import login
import webbrowser
import requests
import base64
import time
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
    
    self.player_Bearer_token = None
    self.devices = None
  
  def _send_command(self, command):
    from_id = self.get_playing_device()
    to_id = from_id
    endpoint = f'https://gew4-spclient.spotify.com/connect-state/v1/player/command/from/{from_id}/to/{to_id}'
    
    data = {
      "command": {
        "endpoint": command
      }
    }
    self.s.post(endpoint, json=data, headers=self.player_headers)
    
  def pause(self):
    self._send_command('pause')
  
  def resume(self):
    self._send_command('resume')
    
  def next_track(self):
    self._send_command('skip_next')
  
  def prev_track(self):
    self._send_command('seek_to')
    
  def set_volume(self, volume):
    url = 'https://gew4-spclient.spotify.com/track-playback/v1/devices/0733d2ccb5a67b5be038642861d8b8a95c727655/volume'
    
    
  def autorize_app(self, app: App, code):
    webbrowser.get('firefox').open_new_tab(f'https://accounts.spotify.com/authorize?client_id={app.client_id}&scope=user-read-playback-state&response_type=code&redirect_uri=http://127.0.0.1:5000/callback')
    
    print('Aspetto il codice Basic')
    # Aspetta che venga chiamata la callback a http://127.0.0.1:5000/callback
    while not code[0]: pass
    
    self.basic_token = code[0]
    
    print(f'Basic token: "{self.basic_token}"')
    
    if self.basic_token:
      url = 'https://accounts.spotify.com/api/token'
      data = {
        'code': self.basic_token,
        'redirect_uri': 'http://127.0.0.1:5000/callback',
        'grant_type': 'authorization_code'
      }
      encoded = base64.b64encode(f'{app.client_id}:{app.client_secret}'.encode()).decode()

      headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + encoded
      }
      
      r = requests.post(url, data=data, headers=headers).json()
      
      if 'access_token' in r:
        self.player_Bearer_token = r['access_token']
        print("Bearer devices token:", self.player_Bearer_token)
      else:
        print("Error: ", r)
    else:
      print("No Basic token")
  
  def get_playing_device(self, update_devices=False):
    if self.devices and not update_devices:
      if self.devices:
        devices = self.devices['devices']
        for device in devices:
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
    if self.player_Bearer_token:
      headers = {
        'Authorization': 'Bearer ' + self.player_Bearer_token
      }
      
      self.devices = requests.get("https://api.spotify.com/v1/me/player/devices", headers=headers).json()
      return self.devices
    else:
      print("Errore nell'otterimento dei dispositivi")
      return None