from flask import Flask, request, render_template
from threading import Thread, Event
from main import main

sp = [None]

ready = Event()

code = [None]

main_process = Thread(target=main, args=(sp, code, ready))
main_process.start()

app = Flask(__name__)

@app.route('/callback', methods=['GET'])
def callback():
  code[0] = request.args.get('code')

  if code[0]:
    return render_template('callback.html', state='App autorizzata con successo')
  else:
    return render_template('callback.html', state='Errore nell\'autorizzazione dell\'app')

@app.route('/resume', methods=['POST'])
def resume():
  if ready.is_set():
    sp[0].resume()
    return 'ok'
  else:
    return 'Backend not ready'

@app.route('/pause', methods=['POST'])
def pause():
  if ready.is_set():
    sp[0].pause()
    return 'ok'
  else:
    return 'Backend not ready'
    
@app.route('/next_track', methods=['POST'])
def next_track():
  if ready.is_set():
    sp[0].next_track()
    return 'ok'
  else:
    return 'Backend not ready'
    
@app.route('/prev_track', methods=['POST'])
def prev_track():
  if ready.is_set():
    sp[0].prev_track()
    return 'ok'
  else:
    return 'Backend not ready'

@app.route('/play_track/<query>', methods=['POST'])
def play_track(query):
  track = sp[0].search_track(query)
  name = track['name']
  uri = track['uri']
  
  sp[0].play_something(uri)
  return name

@app.route('/play_album/<query>', methods=['POST'])
def play_album(query):
  album = sp[0].search_album(query)
  name = album['name']
  uri = album['uri']
  
  sp[0].play_something(uri)
  return name

@app.route('/play_artist/<query>', methods=['POST'])
def play_artist(query):
  artist = sp[0].search_artist(query)
  name = artist['name']
  uri = artist['uri']
  
  sp[0].play_something(uri)
  return name

@app.route('/play_playlist/<query>', methods=['POST'])
def play_playlist(query):
  playlist = sp[0].search_playlist(query)
  name = playlist['name']
  uri = playlist['uri']
  
  sp[0].play_something(uri)
  return name

@app.route('/set_volume/<percentage>', methods=['POST'])
def set_volume(percentage):
  if ready.is_set():
    try:
      percentage = int(percentage)
      
      return 'ok' if sp[0].set_volume(percentage) else 'error'
    except ValueError:
      return 'invalid value for int'
  else:
    return 'Backend not ready'

if __name__ == '__main__':
  # run app in debug mode on port 5000
  app.run(debug=True, port=5000)