from SpotifyClient import SpotifyClient, App
from credentials import username, password
import time

def main(sp, code, ready):
  sp[0] = SpotifyClient(username, password)
  my_app = App(client_id='92fc230dde1c46eeb6ff953580197100', client_secret='cca3aae793dc4922b01650d18d7b3b5b')
  print('Sto autorizzando l\'app')
  sp[0].authorize_app(my_app, code)
  
  ready.set()
  print('Ready')
  
  while True:
    devices = sp[0].update_devices()['devices']
    
    if devices:
      for device in devices:
        if device['is_active']:
          sp[0].save_active_device(device['id'])
    time.sleep(2)