from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random
import sett
import services
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from databases import DatabaseManager
from selenium.common.exceptions import NoSuchElementException

#from multiprocessing import Process
import threading
app = Flask(__name__)

#from selenium.webdriver.common.keys import Keys
import time

def abrir_whatsapp_web():
    options = webdriver.ChromeOptions()
    # Configuración de opciones, por ejemplo, para no mostrar la ventana del navegador
    options.add_argument("user-data-dir=C:/Users/david/AppData/Local/Google/Chrome/User Data")
     #options.add_argument("headless")
    options.add_argument("disable-gpu")
    options.add_argument("no-sandbox")    
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('log-level=3')  # Para reducir la cantidad de logs

         # Deshabilitar imágenes y otros recursos innecesarios
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        #"profile.managed_default_content_settings.cookies": 2,
        "profile.managed_default_content_settings.javascript": 1,
        "profile.managed_default_content_settings.plugins": 1,
        "profile.managed_default_content_settings.popups": 2,
        "profile.managed_default_content_settings.geolocation": 2,
        "profile.managed_default_content_settings.media_stream": 2,
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    
    # Navegar a WhatsApp Web
    driver.get('https://web.whatsapp.com')
    
    print('Abriendo WhatsApp Web...')
    #input("Por favor, escanea el código QR y presiona Enter cuando hayas iniciado sesión...")
    #print('WhatsApp Web cargado.')
    
    return driver

def send_whatsapp_message(numbers, message):
    # Inicializa el navegador web (Chrome en este caso)
    options = webdriver.ChromeOptions()
    
    options.add_argument("user-data-dir=C:/Users/david/AppData/Local/Google/Chrome/User Data")

    #options.add_argument("headless")
    options.add_argument("disable-gpu")
    options.add_argument("no-sandbox")    
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('log-level=3')  # Para reducir la cantidad de logs

       # Deshabilitar imágenes y otros recursos innecesarios
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        #"profile.managed_default_content_settings.cookies": 2,
        "profile.managed_default_content_settings.javascript": 1,
        "profile.managed_default_content_settings.plugins": 1,
        "profile.managed_default_content_settings.popups": 2,
        "profile.managed_default_content_settings.geolocation": 2,
        "profile.managed_default_content_settings.media_stream": 2,
    }
    options.add_experimental_option("prefs", prefs)
    

    driver = webdriver.Chrome(options=options)

    driver.get('https://web.whatsapp.com')

    # Abre WhatsApp Web
    print('Abriendo WhatsApp Web...')
    time.sleep(10)  # Espera 10 segundos para que se cargue WhatsApp Web

    # Espera hasta que el usuario escanee el código QR y cargue WhatsApp Web
    #input("Por favor, escanea el código QR y presiona Enter una vez que hayas iniciado sesión en WhatsApp Web...")

    print('WhatsApp Web cargado.')
 
    for numero in numbers:
        # Construye la URL para enviar el mensaje
        numero = str(numero).replace("(", "").replace(")", "").replace("'", "").replace(",", "").strip()
        url = f"https://web.whatsapp.com/send?phone=593{numero}&text={message}"
        print(f"Navegando a la URL: {url}")
        driver.get(url)
        #input('por favor espere que carge el chat')

        # Espera que se cargue el chat
        time.sleep(15)

        try:

            # Encuentra el cuadro de mensaje y envía el mensaje
            #message_box = driver.find_element(By.XPATH, '#main > footer > div._ak1k._ahmw.copyable-area > div > span:nth-child(2) > div > div._ak1r > div._ak1t._ak1u > button')
            send_button = None
            start_time = time.time()

            while not send_button and time.time() - start_time < 20:  # 60 segundos como tiempo máximo de espera
                try:
                    send_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '#main > footer > div._ak1k._ahmw.copyable-area > div > span:nth-child(2) > div > div._ak1r > div._ak1t._ak1u'))
                    )

                    #send_button = driver.find_element(By.CSS_SELECTOR, '#main > footer > div._ak1k._ahmw.copyable-area > div > span:nth-child(2) > div > div._ak1r > div._ak1t._ak1u')
                except:
                    pass
                wait_time = random.uniform(5, 10)  # Espera entre 1 y 3 segundos antes de volver a comprobar
                                                    # ESPERAR ENTRE 4 Y 7 ahi funciona
                time.sleep(wait_time)
            
            if send_button:
                print('Botón de enviar encontrado.')
                send_button.click()
                print(f"Mensaje enviado al número: {numero}")
            else:
                print(f"Error: No se encontró el botón de enviar para el número {numero} dentro del tiempo permitido.")
        except Exception as e:
            print(f"Error enviando mensaje al número {numero}: {e}")

        # Espera 5 segundos entre cada mensaje para evitar bloqueos
        time.sleep(5)

    # Cierra el navegador después de enviar todos los mensajes
    print('Mensajes enviados exitosamente.')
    driver.quit()

def send_messages_in_background(numbers, message):
    thread = threading.Thread(target=send_whatsapp_message, args=(numbers, message))
    thread.start()
    return thread

def send_bulk_message(nombre):
    db_manager = DatabaseManager()
    db_type = 'postgresql'
    conn = db_manager.connect(db_type)
    numbers = db_manager.envio_masivos_numeros('postgresql', conn)
    text=db_manager.consulta_promociones_descuentos('postgresql',conn,nombre)
    #text = " (POR FAVOR IGNORA ESTOS MENSAJES SON MENSAJES DE PRUEBA Y ERROR)🛍️ ¡Oferta Especial! 🎉\n ¡Descuento del 20% en todos nuestros productos por tiempo limitado! 🎁🎉 Visita nuestra tienda en línea y aprovecha esta increíble oferta. ¿Qué esperas? ¡Contáctanos ya!\n📞 ¡Contáctanos ahora! 📱"
    send_whatsapp_message(numbers,text)

def recordatorio_mensajes_whatsap(numero, message):
    # Inicializa el navegador web (Chrome en este caso)
    options = webdriver.ChromeOptions()
    
    options.add_argument("user-data-dir=C:/Users/david/AppData/Local/Google/Chrome/User Data")

    #options.add_argument("headless")
    options.add_argument("disable-gpu")
    options.add_argument("no-sandbox")    
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('log-level=3')  # Para reducir la cantidad de logs

         # Deshabilitar imágenes y otros recursos innecesarios
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        #"profile.managed_default_content_settings.cookies": 2,
        "profile.managed_default_content_settings.javascript": 1,
        "profile.managed_default_content_settings.plugins": 1,
        "profile.managed_default_content_settings.popups": 2,
        "profile.managed_default_content_settings.geolocation": 2,
        "profile.managed_default_content_settings.media_stream": 2,
    }
    options.add_experimental_option("prefs", prefs)
    

    driver = webdriver.Chrome(options=options)

    driver.get('https://web.whatsapp.com')

    # Abre WhatsApp Web
    print('Abriendo WhatsApp Web...')
    time.sleep(10)  # Espera 10 segundos para que se cargue WhatsApp Web

    # Espera hasta que el usuario escanee el código QR y cargue WhatsApp Web
    #input("Por favor, escanea el código QR y presiona Enter una vez que hayas iniciado sesión en WhatsApp Web...")

    print('WhatsApp Web cargado.')
 
   
        # Construye la URL para enviar el mensaje
    numero = str(numero).replace("(", "").replace(")", "").replace("'", "").replace(",", "").strip()
    url = f"https://web.whatsapp.com/send?phone=593{numero}&text={message}"
    print(f"Navegando a la URL: {url}")
    driver.get(url)
        #input('por favor espere que carge el chat')

        # Espera que se cargue el chat
    time.sleep(15)

    try:
            # Encuentra el cuadro de mensaje y envía el mensaje
            #message_box = driver.find_element(By.XPATH, '#main > footer > div._ak1k._ahmw.copyable-area > div > span:nth-child(2) > div > div._ak1r > div._ak1t._ak1u > button')
        send_button = None
        start_time = time.time()

        while not send_button and time.time() - start_time < 20:  # 60 segundos como tiempo máximo de espera
            try:
                send_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '#main > footer > div._ak1k._ahmw.copyable-area > div > span:nth-child(2) > div > div._ak1r > div._ak1t._ak1u'))
                    )
                    #send_button = driver.find_element(By.CSS_SELECTOR, '#main > footer > div._ak1k._ahmw.copyable-area > div > span:nth-child(2) > div > div._ak1r > div._ak1t._ak1u')
            except:
                pass
            wait_time = random.uniform(5, 10)  # Espera entre 1 y 3 segundos antes de volver a comprobar
                                                    # ESPERAR ENTRE 4 Y 7 ahi funciona
            time.sleep(wait_time)
            
        if send_button:
            print('Botón de enviar encontrado.')
            send_button.click()
            print(f"Mensaje enviado al número: {numero}")
        else:
            print(f"Error: No se encontró el botón de enviar para el número {numero} dentro del tiempo permitido.")
    except Exception as e:
        print(f"Error enviando mensaje al número {numero}: {e}")

        # Espera 5 segundos entre cada mensaje para evitar bloqueos
    time.sleep(5)

    # Cierra el navegador después de enviar todos los mensajes
    print('Mensajes enviados exitosamente.')
    driver.quit()
    