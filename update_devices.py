from credentials import username, password
from SpotifyClient import SpotifyClient
import json

sp = SpotifyClient(username, password)
devices = sp.get_devices()

with open('devices.json', 'w') as file:
  file.write(json.dumps(devices, indent=2))