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
    
    self.player_Bearer_token = None
    self.devices = None
  
  def _send_command(self, command):
    to_id = self.get_playing_device(True)
    
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
    
  def autorize_app(self, app: App, code, open_browser=False):
    if not os.path.exists('.cache') or open_browser:
      url = f'https://accounts.spotify.com/authorize?client_id={app.client_id}&scope=user-read-playback-state&response_type=code&redirect_uri=http://127.0.0.1:5000/callback'
      print('Opening url in browser')
      print('if not open, go to:', url)
      webbrowser.get('firefox').open_new_tab(url)
      
      print('Aspetto il refresh token')
      # Aspetta che venga chiamata la callback a http://127.0.0.1:5000/callback
      while not code[0]: pass
    
      self.refresh_token = code[0]
    else:
      with open('.cache', 'r') as file:
        print('Loading refresh token from .cache')
        self.refresh_token = json.loads(file.read())['refresh_token']
    
    print(f'Refresh token: "{self.refresh_token}"')
    
    if self.refresh_token:
      url = 'https://accounts.spotify.com/api/token'
      data = {
        'code': self.refresh_token,
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
        with open('.cache', 'w') as file:
          data = {
            'access_token': self.player_Bearer_token, 'token_type': 'Bearer',
            'refresh_token': self.refresh_token, 'scope': 'user-read-playback-state'
          }
          json.dump(data, file)
          print(".cache saved")
          
        print("Bearer devices token:", self.player_Bearer_token)
      else:
        print("Error: ", r)
        if r['error'] == 'invalid_grant':
          print('Trying with browser authentication')
          self.autorize_app(app, code, open_browser=True)
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
    if self.player_Bearer_token:
      headers = {
        'Authorization': 'Bearer ' + self.player_Bearer_token
      }
      
      self.devices = requests.get("https://api.spotify.com/v1/me/player/devices", headers=headers).json()
      return self.devices
    else:
      print("Errore nell'otterimento dei dispositivi")
      return None