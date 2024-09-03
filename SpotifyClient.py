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
  
  # TODO: aggiungere un context alla richiesta quando non ci sono dispositivi attivi
  def _send_command(self, data):
    active_device = self.get_playing_device(True)
    
    if self.devices and active_device:
      for device in self.devices['devices']:
        from_id = device['id']
        url = f'https://gew4-spclient.spotify.com/connect-state/v1/player/command/from/{from_id}/to/{active_device}'
        self.s.post(url, json=data, headers=self.player_headers)
    else:
      print('no active device')
    
  def pause(self):
    data = {"command": {"endpoint": 'pause'}}
    self._send_command(data)
  
  def resume(self):
    data = {"command": {"endpoint": 'resume'}}
    self._send_command(data)
    
  def next_track(self):
    data = {"command": {"endpoint": 'skip_next'}}
    self._send_command(data)
  
  def prev_track(self):
    data = {"command": {"endpoint": 'seek_to'}}
    self._send_command(data)
  
  def add_to_queue(self, uri):
    data = {'command': {'endpoint': 'add_to_queue', 'track': {'uri': uri}}}
    self._send_command(data)
    
  def set_volume(self, value):
    active_device = self.get_active_device_id()
    
    if self.devices and active_device:
      for device in self.devices['devices']:
        from_id = device['id']
        url = f'https://gew4-spclient.spotify.com/connect-state/v1/connect/volume/from/{from_id}/to/{active_device}'
        
        data = {
          'volume': round(value / 100.0 * 65535)
        }
        
        self.s.put(url, json=data, headers=self.player_headers)
    else:
      print('no active device')
  
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
    active_device = self.get_active_device_id()
    
    if self.devices and active_device:
      # TODO: interrompere il ciclo quando la richiesta riceve una risposta positiva (anche in set_volume)
      for device in self.devices['devices']:
        from_id = device['id']
      
        url = f'https://gew4-spclient.spotify.com/connect-state/v1/player/command/from/{from_id}/to/{active_device}'
        json = {
          "command": {
            "context": {
              "url": f"context://{uri}"
            },
            "endpoint": "play"
          }
        }

        self.s.post(url, json=json, headers=self.player_headers)
    else:
      print('no active device')
  
  def save_active_device(self, device):
    # Se non esiste il file, lo crea
    if not os.path.exists('active_devices.log'):
      with open('active_devices.log', 'w') as f:
        f.write('[]')
    
    # Carica il file 
    with open('active_devices.log', 'r') as f:
      try:
        devices = json.load(f)
      except json.decoder.JSONDecodeError:
        devices = []
        
    # Cerca il dispositivo e se non c'è lo aggiunge
    if device not in devices:
      devices.append(device)
    
    # Salva le modifiche al file
    with open('active_devices.log', 'w') as f:
      json.dump(devices, f)
  
  def _request_access_token(self, app: App):
    """Gets client credentials access token """
    url = 'https://accounts.spotify.com/api/token'
    
    auth_header = base64.b64encode(f'{app.client_id}:{app.client_secret}'.encode('ascii')).decode('ascii')

    payload = {
      'grant_type': 'authorization_code',
      'code': self.refresh_token,
      'redirect_uri': 'http://127.0.0.1:5000/callback'
    }
    
    headers = {
      'Authorization': f'Basic {auth_header}',
      'Content-Type': 'application/x-www-form-urlencoded'
    }

    print(f"sending POST request to {url} with Headers: {headers} and Body: {payload}")

    try:
      response = self.s.post(
        url,
        data=payload,
        headers=headers
      )
      response.raise_for_status()
      token = response.json()
      return token['access_token']
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
    
    # Qui ho ottenuto il refresh_token
    
    print(f'Refresh token: "{self.refresh_token}"')
    
    if self.refresh_token:
      self.Bearer_token_1 = self._request_access_token(app)
      
      if self.Bearer_token_1:
        print("ho ottenuto con successo il token:",self.Bearer_token_1)
        with open('.cache', 'w') as file:
          data = {
            'access_token': self.Bearer_token_1, 'token_type': 'Bearer',
            'refresh_token': self.refresh_token, 'scope': 'user-read-playback-state'
          }
          json.dump(data, file)
          print(".cache saved")
          
        print("Bearer devices token:", self.Bearer_token_1)
      else:
        print("access_token None")
        self.authorize_app(app, code, open_browser=True)
    else:
      print("No refresh token")
  
  def get_playing_device(self, update_devices=False) -> str:
    if self.devices and not update_devices:
      if self.devices:
        for device in self.devices['devices']:
          if device['is_active']:
            return device['id']
      return None
    else:
      if self.update_devices():
        return self.get_playing_device(False)
      else:
        print("Errore nell'otterimento dei dispositivi")
        return None
  
  def update_devices(self):
    if self.Bearer_token_1:
      headers = {
        'Authorization': 'Bearer ' + self.Bearer_token_1
      }
      
      self.devices = requests.get("https://api.spotify.com/v1/me/player/devices", headers=headers).json()
      return self.devices
    else:
      print("Errore nell'otterimento dei dispositivi")
      return None
  
  def get_device_ids(self):
    if self.devices:
      return [device['id'] for device in self.devices['devices']]
    else:
      return None
  
  # Ritorna l'id del dispositivo attivo o dell'ultimo dispositivo disponibile che è stato attivato
  def get_active_device_id(self):
    active_device = self.get_playing_device(True)
    
    # Se non ci sono dispositivi attivi, attiva l'ultimo usato
    if not active_device:
      print('non ho trovato dispositivi attivi, cerco tra gli ultimi utilizzati')
      with open('active_devices.log', 'r') as f:
        active_devices = json.load(f)
        # Rimuove i nomi dei dispositivi
        active_devices = [device['id'] for device in active_devices]
      
      if active_devices:
        print('ultimi dispositivi utilizzati: ', active_devices)
        dev_found = False
        
        while not dev_found:
          last_active_device = active_devices[-1]
          
          self.update_devices()
          device_ids = self.get_device_ids()
          
          # Se il dispositivo esiste lo seleziona
          if last_active_device in device_ids:
            active_device = last_active_device
            print(f'il dispositivo {last_active_device} esiste, provo ad attivarlo')
            dev_found = True
          else:
            print(f'il dispositivo {last_active_device} non esiste, lo rimuovo')
            active_devices.pop(-1)

        # Salva le modifiche al file
        with open('active_devices.log', 'w') as f:
          json.dump(active_devices, f)
      else:
        print('non ho trovato nessun dispositivo tra gli ultimi utilizzati')
        active_device = None
    print('sto riproducendo sul dispositivo', active_device)
    return active_device