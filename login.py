from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import json


def login(username, password):
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


  driver.get("https://accounts.spotify.com/en/login?continue=https%3A%2F%2Fopen.spotify.com%2F")
  driver.find_element(By.XPATH, '//*[@id="login-username"]').send_keys(username)
  driver.find_element(By.XPATH, '//*[@id="login-password"]').send_keys(password)
  driver.find_element(By.XPATH, '//*[@id="login-button"]').click()
  time.sleep(4)

  # Ottenere l'HTML della pagina
  page_html = driver.page_source
  #time.sleep(60)

  access_token = page_html.find('{"accessToken')
  _ = page_html[access_token:access_token+700]
  _ = _[:_.find('</script>')]
  d = json.loads(_)
  
  access_token = d['accessToken']
  client_id = d['clientId']
  isAnonymous = d['isAnonymous']

  print("access_token:", access_token)
  print("client_id:", client_id)

  if isAnonymous:
    print("Error.")
    return None, None
  else:
    print("Login successful.")
    return f'Bearer {access_token}', client_id