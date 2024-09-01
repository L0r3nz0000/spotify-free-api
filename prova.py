from SpotifyClient import SpotifyClient, App
from credentials import username, password
import requests

refresh_token = None
s = requests.Session()
client_id = '92fc230dde1c46eeb6ff953580197100'
client_secret = 'cca3aae793dc4922b01650d18d7b3b5b'
devices = None
Bearer_token_1 = None

code = [None]

sp = SpotifyClient(username, password)
my_app = App(client_id='92fc230dde1c46eeb6ff953580197100', client_secret='cca3aae793dc4922b01650d18d7b3b5b')
print('Sto autorizzando l\'app')
sp.authorize_app(my_app, code)

while True:
  devices = sp.update_devices()
  
  if devices:
    for device in devices['devices']:
      if device['is_active']: 
        print('> ' + device['name'])
      else:
        print(device['name'])