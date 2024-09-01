from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import threading
import pickle
import time
import json
import os

def login(username, password):
  return_data = []
  
  threading.Thread(target=_login, args=(username, password, return_data)).start()
  while return_data == []:
    time.sleep(0.1)
  return return_data

def _login(username, password, return_data):
  success = False
  
  while not success:
    # Creare un'istanza di ChromeOptions
    chrome_options = Options()

    # Configurare le opzioni (se necessario)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    #chrome_options.add_argument("--disable-dev-shm-usage")
    #chrome_options.add_argument("--disable-gpu")

    # Configurare il servizio ChromeDriver
    service = Service(ChromeDriverManager().install())

    # Inizializzare il driver di Chrome con le opzioni configurate
    driver = webdriver.Chrome(service=service, options=chrome_options)

    if os.path.exists('cookies.pkl'):
      driver.get('https://open.spotify.com')
      
      with open("cookies.pkl", "rb") as file:
        cookies = pickle.load(file)
        for cookie in cookies:
          # Aggiungi ogni cookie al browser
          driver.add_cookie(cookie)
      driver.refresh()
    else:
      driver.get("https://accounts.spotify.com/en/login?continue=https%3A%2F%2Fopen.spotify.com%2F")
      driver.find_element(By.XPATH, '//*[@id="login-username"]').send_keys(username)
      driver.find_element(By.XPATH, '//*[@id="login-password"]').send_keys(password)
      driver.find_element(By.XPATH, '//*[@id="login-button"]').click()
    
    cookies = driver.get_cookies()
    with open("cookies.pkl", "wb") as file:
      pickle.dump(cookies, file)

    # Ottenere l'HTML della pagina
    page_html = driver.page_source
    
    access_token = page_html.find('{"accessToken')
    _ = page_html[access_token:access_token+700]
    _ = _[:_.find('</script>')]
    d = json.loads(_)
    
    access_token = d['accessToken']
    client_id = d['clientId']
    success = d['isAnonymous']

    print("access_token:", access_token)
    print("client_id:", client_id)

    if success:
      print("Error.")
      #driver.close()
      return_data.append(None)
      return_data.append(None)
    else:
      print("Login successful.")
      #driver.close()
      return_data.append(f'Bearer {access_token}')
      return_data.append(client_id)
    
    # Mantiene aperta l'istanza del browser
    while True: pass