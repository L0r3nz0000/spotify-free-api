from threading import Thread, Event
from flask import Flask, request
from main import main
from ctypes import c_char_p
import time

sp = [None]

ready = Event()

code = [None]

main_process = Thread(target=main, args=(sp, code, ready))
main_process.start()

app = Flask(__name__)

@app.route('/callback')
def callback():
  code[0] = request.args.get('code')

  if code[0]:
    return 'App autorizzata con successo'
  else:
    return 'Errore nell\'autorizzazione dell\'app'

@app.route('/resume')
def resume():
  if ready.is_set():
    sp[0].resume()
    return 'ok'
  else:
    return 'Backend not ready'

@app.route('/pause')
def pause():
  if ready.is_set():
    sp[0].pause()
    return 'ok'
  else:
    return 'Backend not ready'
    
@app.route('/next_track')
def next_track():
  if ready.is_set():
    sp[0].next_track()
    return 'ok'
  else:
    return 'Backend not ready'
    
@app.route('/prev_track')
def prev_track():
  if ready.is_set():
    sp[0].prev_track()
    return 'ok'
  else:
    return 'Backend not ready'

@app.route('/set_volume/<percentage>')
def set_volume(percentage):
  if ready.is_set():
    sp[0].set_volume(percentage)
    return 'ok'
  else:
    return 'Backend not ready'

if __name__ == '__main__':
  # run app in debug mode on port 5000
  app.run(debug=True, port=5000)